from django.shortcuts import render, redirect
from rest_framework.views import  APIView
from rest_framework.response import Response
from rest_framework.exceptions import  AuthenticationFailed
#from .serializer  import UserSerializer,UserUpdateSerializer, PasswordUpdateSerializer
from user.models import User  
from posts.models import Posts
from connections.models import Connections
import jwt, datetime
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from random import randint
from django.utils import timezone
import json
from django.core.serializers import serialize
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
import json
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from social_media_platform.utils import authenticate_user


# Create your views here.
class SendRequestView(APIView):
    def get(self, request, user_id):
        try:
            user = authenticate_user(request)   
            
            if str(user._id) == user_id:
                return Response({'error': 'You can not send request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
            target_user = User.objects.filter(_id=user_id).first()
            
            if target_user is None:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            connection = Connections.objects.filter(sender_id=str(user._id), receiver_id=user_id).first()
            if connection is not None:
                return Response({'error': 'Request already sent'}, status=status.HTTP_400_BAD_REQUEST)

            connection = Connections.objects.create(sender_id=str(user._id), receiver_id=user_id)
            connection.save()
            
            
            
            return Response({'message': 'Request sent successfully'}, status=status.HTTP_200_OK)
            

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class AcceptRequestView(APIView):
    def get(self, request, connection_id):
        try:
            user = authenticate_user(request)   
            
            
            connection = Connections.objects.get(_id=connection_id)
            
            if connection is None:
                return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if connection.receiver_id != str(user._id):
                return Response({'error': 'You are not authorized to accept this request'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if connection.is_accepted:
                return Response({'error': 'Request already accepted'}, status=status.HTTP_400_BAD_REQUEST)
            
            connection.is_accepted = True 
            connection.accepted_dateTime = timezone.now()

            connection.save()
            
            sender = User.objects.get(_id=connection.sender_id)
            receiver = User.objects.get(_id=connection.receiver_id)
            
            sender.connected_user_ids.append(str(receiver._id))
            receiver.connected_user_ids.append(str(sender._id))
            
            sender.save()
            receiver.save()
            
            
            return Response({'message': 'Request accepted successfully'}, status=status.HTTP_200_OK)
            

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

class CancleRequestView(APIView):
    def get(self, request, connection_id):
        try:
            user = authenticate_user(request)   
            
            
            connection = Connections.objects.get(_id=connection_id)
            
            if connection is None:
                return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)


            sender = User.objects.get(_id=connection.sender_id)
            receiver = User.objects.get(_id=connection.receiver_id)
            
            sender.connected_user_ids.remove(str(receiver._id))
            receiver.connected_user_ids.remove(str(sender._id))
            
            sender.save()
            receiver.save()
            
            connection.delete()
            
            if connection.is_accepted:
                return Response({'message': 'Unfriended successfully'}, status=status.HTTP_200_OK)
            
            return Response({'message': 'Request deleted successfully'}, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)           
        
        
        
class AllConnectionsView(APIView):
    def get(self, request):
        try:
            user = authenticate_user(request)   
            
            connections = Connections.objects.filter(Q(sender_id=str(user._id)) | Q(receiver_id=str(user._id)))
            
            formatted_connections = []
            
            for connection in connections:
                formatted_connection = {
                    '_id': connection._id,
                    'is_accepted': connection.is_accepted,
                    'accepted_dateTime': connection.accepted_dateTime,
                    'sender': User.objects.filter(_id=connection.sender_id).first().get_formatted_data(),
                    'receiver': User.objects.filter(_id=connection.receiver_id).first().get_formatted_data(),
                    'created_dateTime': connection.created_dateTime
                }
                formatted_connections.append(formatted_connection)
            
            page = request.GET.get('page')
            size = request.GET.get('size')   
            
            if (page is None and size is not None) or (page is not None and size is None):
                return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)

            page = int(page) if page is not None and page.isdigit() else 1
            size = int(size) if size is not None and size.isdigit() else None    
            
            
            if size:
                paginator = Paginator(formatted_connections, size)
                try:
                    formatted_connections = paginator.page(page)
                except EmptyPage:
                    return Response([])

                total_elements = paginator.count
                total_pages = paginator.num_pages
                has_next = formatted_connections.has_next()
                has_previous = formatted_connections.has_previous


                response_data = {
                    'data': list(formatted_connections) ,
                    'first_page': 1,
                    'next_page': page + 1 if has_next else None,
                    'total_elements': total_elements,
                    'last_page': total_pages
                }

            if not size:
                response_data = {
                    'data': formatted_connections,
                    'first_page': 1,
                    'next_page': None,
                    'total_elements': len(formatted_connections),
                    'last_page': None
                }
                
            return Response(response_data, status=status.HTTP_200_OK)                          
                        

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class AllConnectionsByNameView(APIView):
    def get(self, request, user_name):
        try:
            user = authenticate_user(request)   
            
            connections = Connections.objects.filter(Q(sender_id=str(user._id)) | Q(receiver_id=str(user._id)))
            
            searched_connections = []
            
            for connection in connections:
                sender = User.objects.filter(_id=connection.sender_id).first()
                receiver = User.objects.filter(_id=connection.receiver_id).first()
                
                if user_name.lower() in sender.name.lower() or  user_name.lower() in receiver.name.lower() :
                    searched_connections.append(connection)

            
            formatted_connections = []
            
            for connection in searched_connections:
                formatted_connection = {
                    '_id': connection._id,
                    'is_accepted': connection.is_accepted,
                    'accepted_dateTime': connection.accepted_dateTime,
                    'sender': User.objects.filter(_id=connection.sender_id).first().get_formatted_data(),
                    'receiver': User.objects.filter(_id=connection.receiver_id).first().get_formatted_data(),
                    'created_dateTime': connection.created_dateTime
                }
                formatted_connections.append(formatted_connection)
            
            page = request.GET.get('page')
            size = request.GET.get('size')   
            
            if (page is None and size is not None) or (page is not None and size is None):
                return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)
            
            page = int(page) if page is not None and page.isdigit() else 1
            size = int(size) if size is not None and size.isdigit() else None    
            
            
            if size:
                paginator = Paginator(formatted_connections, size)
                try:
                    formatted_connections = paginator.page(page)
                except EmptyPage:
                    return Response([])

                total_elements = paginator.count
                total_pages = paginator.num_pages
                has_next = formatted_connections.has_next()
                has_previous = formatted_connections.has_previous


                response_data = {
                    'data': list(formatted_connections) ,
                    'first_page': 1,
                    'next_page': page + 1 if has_next else None,
                    'total_elements': total_elements,
                    'last_page': total_pages
                }

            if not size:
                response_data = {
                    'data': formatted_connections,
                    'first_page': 1,
                    'next_page': None,
                    'total_elements': len(formatted_connections),
                    'last_page': None
                }
                
            return Response(response_data, status=status.HTTP_200_OK)                          
                        

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
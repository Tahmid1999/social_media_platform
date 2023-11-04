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
import random


# Create your views here.
class FeedShowView(APIView):
    def get(self, request):
        try:
            # Get the Bearer token from the Authorization header
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                raise AuthenticationFailed('Authentication credentials were not provided.')

            # The Authorization header should have a value like "Bearer <token>"
            # Extract the token part after "Bearer "
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                raise AuthenticationFailed('Invalid token format')

            try:
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Token has expired.')
            except jwt.DecodeError:
                raise AuthenticationFailed('Token is invalid.')


            user = User.objects.filter(_id=payload['id']).first()
            
            if user is None:
                raise AuthenticationFailed('Token is invalid.')
            
            # Check if the token is in the user's logged_in_tokens
            token_found = False
            for token_entry in user.logged_in_tokens:
                if token_entry['token'] == token:
                    token_found = True
                    break        
            
            if not token_found:
                raise AuthenticationFailed('Token is invalid.')    
            
            
            connections = Connections.objects.filter(Q(sender_id=str(user._id)) | Q(receiver_id=str(user._id)))
            
            accepted_connections = [connection for connection in connections if connection.is_accepted]

            user_ids = []
            
            for connection in accepted_connections:
                if connection.sender_id == str(user._id):
                    user_ids.append(connection.receiver_id)
                else:
                    user_ids.append(connection.sender_id)
                    
            user_ids = list(set(user_ids))
            
            
            all_posts = Posts.objects.filter(creator_user_id__in=user_ids).order_by('-created_dateTime')

            
            formated_post = []

            for post in all_posts:  
                latest_comment = post.comments[-1] if len(post.comments) > 0 else None
                orginal_post_json = None
                
                if post.is_shared == True:
                    orginal_post = Posts.objects.filter(_id=post.original_post_id).first()
                                
                    if orginal_post is not None:
                        orginal_post_json = {
                            'id': orginal_post._id,
                            'text': orginal_post.text,
                            'images': orginal_post.images,
                            'keywords': orginal_post.kewords,
                            'created_dateTime': orginal_post.created_dateTime,
                            'orginal_creator': User.objects.get(_id=orginal_post.orginal_creator_user_id).get_formatted_data(),
                            'likes': len(orginal_post.likes),
                            'shares_count': orginal_post.share_count                   
                        }
                    
                
                formated_post.append({
                    'is_shared': post.is_shared,

                    'post_id': post._id,
                    'creator' : User.objects.get(_id=post.creator_user_id).get_formatted_data(),
                    'text': post.text if post.is_shared == False else None,
                    'images': post.images if post.is_shared == False else None,
                    'keywords': post.kewords if post.is_shared == False else None,
                    'created_dateTime': post.created_dateTime,
                    'likes': len(post.likes),
                    'latest_comments': {
                        'comment_id': latest_comment['_id'] if latest_comment is not None else None,
                        'user': User.objects.get(_id=latest_comment['comment_by']).get_formatted_data() if latest_comment is not None else None,
                        'text': latest_comment['comment'] if latest_comment is not None else None,
                        'comment_likes': len(latest_comment['comment_likes']) if latest_comment is not None else None,
                        'datetime': latest_comment['datetime']  if latest_comment is not None else None,
                    },
                    'shares_count': post.share_count,
                        
                    'orginal_post_details': orginal_post_json
                })   
                
            random.shuffle(formated_post)
            
            page = request.GET.get('page')
            size = request.GET.get('size')
            
            
            if (page is None and size is not None) or (page is not None and size is None):
                return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)

            page = int(page) if page is not None and page.isdigit() else 1
            size = int(size) if size is not None and size.isdigit() else None
            

            if size:
                paginator = Paginator(formated_post, size)
                try:
                    formated_post = paginator.page(page)
                except EmptyPage:
                    return Response([])

                total_elements = paginator.count
                total_pages = paginator.num_pages
                has_next = formated_post.has_next()
                has_previous = formated_post.has_previous
                

                response_data = {
                    'data': list(formated_post),
                    'first_page': 1,
                    'next_page': page + 1 if has_next else None,
                    'total_elements': total_elements,
                    'last_page': total_pages
                }            
                
            if not size:
                response_data = {
                    'data': formated_post,
                    'first_page': 1,
                    'next_page': None,
                    'total_elements': len(formated_post),
                    'last_page': None
                }
            
            return Response(response_data)                         
                    
                        
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
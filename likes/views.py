from django.shortcuts import render, redirect
from rest_framework.views import  APIView
from rest_framework.response import Response
from rest_framework.exceptions import  AuthenticationFailed
#from .serializer  import UserSerializer,UserUpdateSerializer, PasswordUpdateSerializer
from user.models import User  
from posts.models import Posts
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
from social_media_platform.utils import authenticate_user



# Create your views here.
class LikePostView(APIView):
    def get(self, request, post_id):
        try:
            user = authenticate_user(request)   
            
            post = Posts.objects.get(_id=post_id)
            
            if post is None:
                return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)

            creator = User.objects.get(_id=post.orginal_creator_user_id)
            
            if creator is None:
                return Response({'message': 'Post creator not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            if creator._id != user._id and creator.is_locked and str(creator._id) not in user.connected_user_ids:
                return Response({'message': 'This post is from locked profile.'}, status=status.HTTP_403_FORBIDDEN)
                        
            
            for like in post.likes:
                if like['user_id'] == str(user._id):
                    post.likes.remove(like)
                    post.save()
                    return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)    
            
            post.likes.append({
                'user_id': str(user._id),
                'dateTime': timezone.now()
            })
            
            post.save()
            
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'message': 'Invalid post id!'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AllLikesView(APIView):
    def get(self, request, post_id):
        try:
            user = authenticate_user(request) 
            
            post = Posts.objects.get(_id=post_id)
                
            if post is None:
                return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)

            creator = User.objects.get(_id=post.orginal_creator_user_id)
            
            if creator is None:
                return Response({'message': 'Post creator not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            if creator._id != user._id and creator.is_locked and str(creator._id) not in user.connected_user_ids:
                return Response({'message': 'This post is from locked profile.'}, status=status.HTTP_403_FORBIDDEN)
            
            
            likes = post.likes
            
            formatted_likes = []
            
            for like in likes:
                formatted_likes.append({
                    'user_id': like['user_id'], 
                    'username': User.objects.get(_id=like['user_id']).name,
                    'profile_pic': User.objects.get(_id=like['user_id']).profile.get('profile_picture'),
                    'datetime': like['dateTime']
                })
                
            page = request.GET.get('page')
            size = request.GET.get('size')        
        
            formatted_data = []

            
            if (page is None and size is not None) or (page is not None and size is None):
                return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)

            page = int(page) if page is not None and page.isdigit() else 1
            size = int(size) if size is not None and size.isdigit() else None    
            
            
            if size:
                paginator = Paginator(formatted_likes, size)
                try:
                    formatted_likes = paginator.page(page)
                except EmptyPage:
                    return Response([])

                total_elements = paginator.count
                total_pages = paginator.num_pages
                has_next = formatted_likes.has_next()
                has_previous = formatted_likes.has_previous

                formatted_data = list(formatted_likes) 

                response_data = {
                    'data': formatted_data,
                    'first_page': 1,
                    'next_page': page + 1 if has_next else None,
                    'total_elements': total_elements,
                    'last_page': total_pages
                }

            if not size:
                response_data = {
                    'data': formatted_likes,
                    'first_page': 1,
                    'next_page': None,
                    'total_elements': len(formatted_likes),
                    'last_page': None
                }
                
            return Response(response_data, status=status.HTTP_200_OK)    
        
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)     
        except ValidationError as e:
            return Response({'message': 'Invalid post id!'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
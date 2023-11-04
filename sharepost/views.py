from django.shortcuts import render

# Create your views here.
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
class CreateSharedPostView(APIView):
    def get(self, request, post_id):
        user = authenticate_user(request)
        
        try:  
            post = Posts.objects.get(_id=post_id)
            
            if post is None:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            
            creator = User.objects.get(_id=post.creator_user_id)
            
            if creator is None:
                return Response({'error': 'Post creator not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if creator.is_locked:
                return Response({'error': 'This profile is locked. You can not share this creator posts.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if post.is_shared:                   
                my_post = Posts(is_shared = True, original_post_id = post.original_post_id, creator_user_id = user._id, orginal_creator_user_id = post.orginal_creator_user_id)
                my_post.save()
                
                
                post.share_count += 1
                post.save()
                
                original_post = Posts.objects.get(_id=post.original_post_id)
                original_post.share_count += 1
                original_post.save()
                
                
                return Response({'message': 'Post shared successfully'}, status=status.HTTP_201_CREATED)
            
            else:
                my_post = Posts(is_shared = True, original_post_id = post_id, creator_user_id = user._id, orginal_creator_user_id = post.orginal_creator_user_id)
                my_post.save()
                
                original_post = Posts.objects.get(_id=post_id)
                original_post.share_count += 1
                original_post.save()
                

                return Response({'message': 'Post shared successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
from django.shortcuts import render, redirect
from rest_framework.views import  APIView
from rest_framework.response import Response
from rest_framework.exceptions import  AuthenticationFailed
#from .serializer  import UserSerializer,UserUpdateSerializer, PasswordUpdateSerializer
from user.models import User  
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
from social_media_platform.utils import authenticate_user


# Create your views here.
class UserProfileView(APIView):
    def post(self, request):
        user = authenticate_user(request)
        
        profile_picture = request.FILES.get('profile_picture')
        cover_picture = request.FILES.get('cover_picture')
        dob = request.data.get('dob')    
        bio = request.data.get('bio')
        social_media_links = request.data.get('social_media_links')
        
        if profile_picture:
            fs = FileSystemStorage()
            allowed_extensions = ['.jpeg', '.jpg', '.png']
            file_extension = '.'+profile_picture.name.lower().split('.')[-1]
            
            if file_extension not in allowed_extensions:
                #raise ValidationError('Invalid file format. Allowed formats: JPEG, JPG, PNG.')
                return Response({'message': 'Invalid file format. Allowed formats: JPEG, JPG, PNG.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use the user's _id as part of the file name for the profile picture
            filename = f"{user._id}_propic{file_extension}"                        


            uploaded_file_name = fs.save(filename, profile_picture)
            
            uploaded_file_url = fs.url(uploaded_file_name)
                        
            user.profile['profile_picture'] = uploaded_file_url
        
        
        if cover_picture:
            fs = FileSystemStorage()
            allowed_extensions = ['.jpeg', '.jpg', '.png']
            file_extension = '.'+cover_picture.name.lower().split('.')[-1]
            
            if file_extension not in allowed_extensions:
                #raise ValidationError('Invalid file format. Allowed formats: JPEG, JPG, PNG.')
                return Response({'message': 'Invalid file format. Allowed formats: JPEG, JPG, PNG.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use the user's _id as part of the file name for the profile picture
            filename = f"{user._id}_coverpic{file_extension}"                        


            uploaded_file_name = fs.save(filename, cover_picture)
            
            uploaded_file_url = fs.url(uploaded_file_name)
                        
            user.profile['cover_picture'] = uploaded_file_url
            
        
        if dob:
            # Check if the date is in the correct format (YYYY-MM-DD)
            try:
                datetime.datetime.strptime(dob, '%Y-%m-%d')
            except ValueError:
                return Response({'message': 'Invalid date format. Date format should be YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.profile['dob'] = dob
        
        if bio:
            user.profile['bio'] = bio
        
        if social_media_links:
            social_media_links = json.loads(social_media_links)
            
            
            try:
                if user.profile['social_media_links'] is None:
                    user.profile['social_media_links'] = []
            except KeyError:
                user.profile['social_media_links'] = []

            for social_media_link in social_media_links:
                if social_media_link['name'] is None or social_media_link['url'] is None:
                    continue
                
                social_media_link_found = False
                for user_social_media_link in user.profile['social_media_links']:
                    if user_social_media_link['name'] == social_media_link['name']:
                        user_social_media_link['url'] = social_media_link['url']
                        social_media_link_found = True
                        break
                
                if not social_media_link_found:
                    user.profile['social_media_links'].append(social_media_link)
                    
                    
            user.profile['social_media_links'] = social_media_links
            
        user.save()
        return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)
    
    def get(self, request):
        user = authenticate_user(request)
        
        return Response(user.get_user_data(), status=status.HTTP_200_OK)        
        

class OtherUserProfileView(APIView):
    def get(self, request, user_id):
        user = authenticate_user(request)
        
        other_user = User.objects.filter(_id=user_id).first()
        
        if not other_user:
            raise AuthenticationFailed('User not found.')
        
        return Response(other_user.get_user_data(), status=status.HTTP_200_OK)
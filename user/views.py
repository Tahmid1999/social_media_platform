from django.shortcuts import render, redirect
from rest_framework.views import  APIView
from rest_framework.response import Response
from rest_framework.exceptions import  AuthenticationFailed
from .serializer  import UserSerializer,UserUpdateSerializer, PasswordUpdateSerializer
from .models import User  
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
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from social_media_platform.utils import authenticate_user


# Create your views here.
# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            # Check if a user with the same email already exists
            user = User.objects.filter(email=email).first()

            if user is not None and user.is_verified == True:
                return Response({'message': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            elif user is not None and user.is_verified == False:
                User.objects.filter(email=email).delete()
                    
            
            bypass_verification = request.GET.get('bypass_verification')
            
            if bypass_verification is not None and bypass_verification == 'true':
                try:            
                    random_number = str(randint(10000, 99999))
                    timestamp = timezone.now()

                    user_data = {
                        'email': request.data.get('email'),
                        'name': request.data.get('name'),
                        'password': request.data.get('password'),
                        'country': request.data.get('country'),
                        'city': request.data.get('city'),
                        'email_verify_token': random_number,
                        'email_verify_token_dateTime': timestamp,
                        'is_verified': True,
                        'verified_dateTime': timezone.now()
                    }              

                    serializer = UserSerializer(data=user_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        
                    
                    return Response({'message': 'Account is created.'}, status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({'message': 'Please try again'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    random_number = str(randint(10000, 99999))
                    timestamp = timezone.now()
                    
                    user_data = {
                        'email': request.data.get('email'),
                        'name': request.data.get('name'),
                        'password': request.data.get('password'),
                        'country': request.data.get('country'),
                        'city': request.data.get('city'),
                        'email_verify_token': random_number,
                        'email_verify_token_dateTime': timestamp,
                    }                   
                    
                    # Send an email
                    subject = 'Account Verification'
                    message = f'Your account verification code  is  {random_number}. This is valid for 10  minuits.'
                    from_email = 'deepbluesubscriptions@gmail.com'
                    recipient_list = [email]  # Change this to get the recipient's email

                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)       

                    serializer = UserSerializer(data=user_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    
                    return Response({'message': 'Verify the email'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'message': 'Please try again'}, status=status.HTTP_400_BAD_REQUEST)                
        except Exception as e:
            return Response({'message': 'Please try again'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')

        try:
            user = User.objects.get(email=email)


            if user.is_verified:
                return Response({'message': 'Email already verified'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user == None:
                return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.email_verify_token == token:
                if timezone.now() - user.email_verify_token_dateTime > datetime.timedelta(minutes=10):
                    return Response({'message': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.is_verified = True
                    user.verified_dateTime = timezone.now()
                    user.save()
                    return Response({'message': 'Email verified'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)


class CheckEmailExsistOrNotView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        
        if user is None or user.is_verified == False:
            return Response({'message': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                random_number = str(randint(10000, 99999))
                timestamp = timezone.now()
                
                subject = 'Password Reset'
                message = f'Your reset password code  is  {random_number}. This is valid for 10  minuits.'
                from_email = 'deepbluesubscriptions@gmail.com'
                recipient_list = [email]  # Change this to get the recipient's email

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)  
                
                user.forgot_password_token = random_number
                user.forgot_password_token_dateTime = timestamp
                user.save()            
                return Response({'message': 'Email found'}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({'message': 'Please try again'}, status=status.HTTP_400_BAD_REQUEST)

class PassResetOtpCheckView(APIView):
    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')
        
        try:
            user = User.objects.get(email=email)
            
            if user == None:
                return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.forgot_password_token == token:
                if timezone.now() - user.forgot_password_token_dateTime > datetime.timedelta(minutes=10):
                    return Response({'message': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Token is correct'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

class PassResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            
            if user == None:
                return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.forgot_password_token == token:
                if timezone.now() - user.forgot_password_token_dateTime > datetime.timedelta(minutes=10):
                    return Response({'message': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(password)
                    user.save()
                    return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)   
            
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': str(user._id),  # Convert ObjectId to a string
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=15),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Initialize the logged_in_tokens array if it's None
        if user.logged_in_tokens is None:
            user.logged_in_tokens = []

        # Append the new token to the logged_in_tokens array
        user.logged_in_tokens.append({
            'token': token,
            'created_datetime': timezone.now()
        })

        user.save()  # Save the user to persist the updated tokens array

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'is_admin': user.is_superuser
        }
        return response

class UserView(APIView):
    def get(self, request):
        user = authenticate_user(request)
        
        formatted_data = user.get_formatted_data()
        return Response(formatted_data)
    
    def put(self, request):
        user = authenticate_user(request)
        
        # Validate and update the user data
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            formatted_data = user.get_formatted_data()
            return Response(formatted_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordUpdateView(APIView):
    def post(self, request):
        user = authenticate_user(request)

        serializer = PasswordUpdateSerializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']

            # Verify the current password
            if not user.check_password(current_password):
                return Response({'message': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            # Change the password
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserListView(APIView):
    def get(self, request):
        user = authenticate_user(request)
                
        page = request.GET.get('page')
        size = request.GET.get('size')
        
        if (page is None and size is not None) or (page is not None and size is None):
            return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)

        page = int(page) if page is not None and page.isdigit() else 1
        size = int(size) if size is not None and size.isdigit() else None

        formatted_data = []
        users = User.objects.all()

        if size:
            paginator = Paginator(users, size)
            try:
                users = paginator.page(page)
            except EmptyPage:
                return Response([])  

            total_elements = paginator.count
            total_pages = paginator.num_pages
            has_next = users.has_next()
            has_previous = users.has_previous

            formatted_data = [user.get_formatted_data() for user in users]

            response_data = {
                'data': formatted_data,
                'first_page': 1,
                'next_page': page + 1 if has_next else None,
                'total_elements': total_elements,
                'last_page': total_pages
            }

        if not size:
            for user in users:
                formatted_data.append(user.get_formatted_data())
                
            response_data = {
                'data': formatted_data,
                'first_page': 1,
                'next_page': None,
                'total_elements': len(formatted_data),
                'last_page': None
            }    
        return Response(response_data)
        
class UserSearchView(APIView):
    def post(self, request):
        user = authenticate_user(request)

        # Get the search query from the request data
        search_query = request.data.get('search_query')

        if not search_query:
            return Response({'message': 'Search query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Perform a case-insensitive search for users by name
        users = User.objects.filter(
            Q(name__icontains=search_query)
        )

        page = request.GET.get('page')
        size = request.GET.get('size')
        
        
        formatted_data = []

        
        if (page is None and size is not None) or (page is not None and size is None):
            return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)

        page = int(page) if page is not None and page.isdigit() else 1
        size = int(size) if size is not None and size.isdigit() else None
        

        if size:
            paginator = Paginator(users, size)
            try:
                users = paginator.page(page)
            except EmptyPage:
                return Response([])

            total_elements = paginator.count
            total_pages = paginator.num_pages
            has_next = users.has_next()
            has_previous = users.has_previous

            formatted_data = [user.get_formatted_data() for user in users]

            response_data = {
                'data': formatted_data,
                'first_page': 1,
                'next_page': page + 1 if has_next else None,
                'total_elements': total_elements,
                'last_page': total_pages
            }

        if not size:
            for user in users:
                formatted_data.append(user.get_formatted_data())

            response_data = {
                'data': formatted_data,
                'first_page': 1,
                'next_page': None,
                'total_elements': len(formatted_data),
                'last_page': None
            }

        return Response(response_data)
    
class UserLockView(APIView):
    def get(self, request):
        user = authenticate_user(request)
        
        user.is_locked = True
        user.locked_dateTime = timezone.now()
        user.save()
        
        return Response({'message': 'User locked successfully.'}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        user = authenticate_user(request)
        
        user.is_locked = False
        user.locked_dateTime = None
        user.save()
        
        return Response({'message': 'User unlocked successfully.'}, status=status.HTTP_200_OK)
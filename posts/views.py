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
from django.db.models import Q
from social_media_platform.utils import authenticate_user


# Create your views here.
class PostCreateView(APIView):
    def post(self, request):
        try:
            user = authenticate_user(request)    
            
            text = request.data.get('text')
            images = request.FILES.getlist('images')
            keywords = request.data.get('keywords')
            
            try:  
                post_images = []
                
                if (text is None or text == '') and (images is None or len(images) == 0):
                    return Response({'error': 'You need to  put  text  or  image'}, status=status.HTTP_400_BAD_REQUEST) 
                
                if keywords is None or len(keywords) == 0:
                    return Response({'error': 'You need to add keywords'}, status=status.HTTP_400_BAD_REQUEST)
                
                
                if images is not None:
                    if len(images) > 5:
                        return Response({'error': 'You can only upload 5 images'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        for image in images:
                            if image.size > 1000000:
                                return Response({'error': 'Image size should not be greater than 1MB'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            fs = FileSystemStorage()
                            allowed_extensions = ['.jpeg', '.jpg', '.png']
                            file_extension = '.'+image.name.lower().split('.')[-1]
                            
                            if file_extension not in allowed_extensions:
                                return Response({'error': 'Invalid file format. Allowed formats: JPEG, JPG, PNG.'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            now = datetime.datetime.now()
                            date_string = now.strftime('%Y%m%d%H%M%S')

                            # Use the user's _id as part of the file name for the image
                            filename = f"{user._id}_{randint(1000000, 9999999)}_{date_string}{file_extension}"
                            uploaded_file_name = fs.save(filename, image)
                            image_url = fs.url(uploaded_file_name)
                            
                            post_images.append(image_url)
                            
                if keywords is not None:
                    keywords = json.loads(keywords)

                    if len(keywords) != len(set(keywords)):
                        return Response({'error': 'You cannot add duplicate keywords'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if len(keywords) > 5:
                        return Response({'error': 'You can only add 5 keywords'}, status=status.HTTP_400_BAD_REQUEST)
                    
            
                            
                    post = Posts(orginal_creator_user_id=user._id, creator_user_id = user._id,  text=text, images=post_images, kewords=keywords)
                    post.save()
                    
                    
                    return Response({'message': 'Post created successfully'}, status=status.HTTP_201_CREATED)
            except:
                return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                  
class PostUpdateView(APIView):
    def put(self, request, post_id):
        try:
            user = authenticate_user(request)   
            
            text = request.data.get('text')
            images = request.FILES.getlist('images')
            
            try:
                post_images = []
                
                post = Posts.objects.filter(_id=post_id).first()
                
                if post is None:
                    return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
                
                if post.orginal_creator_user_id != user._id:
                    return Response({'error': 'You are not authorized to update this post'}, status=status.HTTP_401_UNAUTHORIZED)

                
                if (text is None or text == '') and (images is None or len(images) == 0):
                    return Response({'error': 'You need to  put  text  or  image'}, status=status.HTTP_400_BAD_REQUEST)
                
                if images is not None:
                    if len(images) > 5:
                        return Response({'error': 'You can only upload 5 images'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        for image in images:
                            if image.size > 1000000:
                                return Response({'error': 'Image size should not be greater than 1MB'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            fs = FileSystemStorage()
                            allowed_extensions = ['.jpeg', '.jpg', '.png']
                            file_extension = '.'+image.name.lower().split('.')[-1]
                            
                            if file_extension not in allowed_extensions:
                                return Response({'error': 'Invalid file format. Allowed formats: JPEG, JPG, PNG.'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            now = datetime.datetime.now()
                            date_string = now.strftime('%Y%m%d%H%M%S')

                            # Use the user's _id as part of the file name for the image
                            filename = f"{user._id}_{randint(1000000, 9999999)}_{date_string}{file_extension}"
                            uploaded_file_name = fs.save(filename, image)
                            image_url = fs.url(uploaded_file_name)
                            
                            post_images.append(image_url)
                            post.images = post_images
                            post.save()

                            

                    if text is not None and text != '':         
                        post.text = text
                        post.save()
                    

                    if keywords is not None:
                        keywords = json.loads(keywords)

                        if len(keywords) != len(set(keywords)):
                            return Response({'error': 'You cannot add duplicate keywords'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        if len(keywords) > 5:
                            return Response({'error': 'You can only add 5 keywords'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        post.kewords = keywords
                        post.save()
                                    
                    return Response({'message':  'Post updated successfully'}, status=status.HTTP_200_OK)   
            except:
                return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                                                                                               
class PostDeleteView(APIView):
    def delete(self, request, post_id):
        try:
            user = authenticate_user(request)   
            
            try:
                post = Posts.objects.filter(_id=post_id).first()
                
                if post is None:
                    return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
                
                if post.orginal_creator_user_id != user._id:
                    return Response({'error': 'You are not authorized to delete this post'}, status=status.HTTP_401_UNAUTHORIZED)
                
                post.delete()
                
                return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)
            except:
                return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)               
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
                
class PostByIdView(APIView):
    def get(self, request, post_id):
        user = authenticate_user(request)   
        
        try:
            post = Posts.objects.filter(_id=post_id).first()
            
            if post is None:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            
            creator = User.objects.get(_id=post.orginal_creator_user_id)
            
            if creator is None:
                return Response({'error': 'Creator not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if user._id != creator._id and  creator.is_locked == True and str(creator._id) not in user.connected_user_ids:
                    return Response({'error': 'The creator account is private. To see this post you need to be his friend.'}, status=status.HTTP_401_UNAUTHORIZED)

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
                             
            post_data = {
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
                }
            
            return Response(post_data, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)               
              
class SelfAllPostView(APIView):
    def get(self, request):
        try:
            user = authenticate_user(request)   

            all_posts = Posts.objects.filter(creator_user_id =user._id).order_by('-created_dateTime')
                    
            formated_post = []

            for post in all_posts:  
                latest_comment = post.comments[-1] if len(post.comments) > 0 else None
                orginal_post_json = None
                
                if post.is_shared == True:
                    orginal_post = Posts.objects.filter(_id=post.original_post_id).first()
                    
                    if user._id != post.orginal_creator_user_id and User.objects.get(_id=post.orginal_creator_user_id).is_locked == True and str(post.orginal_creator_user_id) not in user.connected_user_ids:     
                        orginal_post_json = None       
                    
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
                    'data': formated_post,
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
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
class SearchByKeywordView(APIView):
    def get(self, request, keyword):
        try:
            user = authenticate_user(request)   
            
            filtered_posts = Posts.objects.filter(
                Q(kewords__icontains=keyword) |
                Q(kewords__icontains=keyword.lower()) |
                Q(kewords__icontains=keyword.upper())
            ).order_by('-created_dateTime')

            formated_post = []

            for post in filtered_posts:  
                if user._id != post.orginal_creator_user_id and User.objects.get(_id=post.orginal_creator_user_id).is_locked == True and str(post.orginal_creator_user_id) not in user.connected_user_ids:
                    continue
                else:    
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
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class OtherAllPostView(APIView):
    def get(self, request, user_id):
        try:
            user = authenticate_user(request)   
            
            post_user = User.objects.filter(_id=user_id).first()
                
            if post_user is None:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if user._id != post_user._id and post_user.is_locked == True and str(post_user._id) not in user.connected_user_ids:
                return Response({'error': 'The user account is locked. To see this post you need to be his friend.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            all_posts = Posts.objects.filter(creator_user_id =post_user._id).order_by('-created_dateTime')
                    
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
        
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
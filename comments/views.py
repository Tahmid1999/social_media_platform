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
import uuid
from social_media_platform.utils import authenticate_user


# Create your views here.
class CreateCommentView(APIView):
    def post(self, request, post_id):
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
                       
            comment = request.data.get('comment')
            
            if not comment:
                return Response({'message': 'Comment is required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            comment = {
                '_id': uuid.uuid4(),
                'comment': comment,
                'comment_by': user._id,
                'comment_likes': [],
                'datetime': timezone.now()
            }
            post.comments.append(comment)
            post.save()
            return Response({'message': 'Comment created successfully!'}, status=status.HTTP_201_CREATED)
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CommentUpdateView(APIView):
    def put(self, request, post_id, comment_id):
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
            
            
            comment = request.data.get('comment')
            
            if not comment_id:
                return Response({'message': 'Comment ID is required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not comment:
                return Response({'message': 'Comment is required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            comment_found = False
            for comment_entry in post.comments:
                if str(comment_entry['_id']) == comment_id:
                    comment_found = True
                    comment_entry['comment'] = comment
                    comment_entry['datetime'] = timezone.now()
                    break
            
            if not comment_found:
                return Response({'message': 'Comment not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            post.save()
            return Response({'message': 'Comment updated successfully!'}, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CommentDeleteView(APIView):
    def delete(self, request, post_id, comment_id):
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
            
                        
            if not comment_id:
                return Response({'message': 'Comment ID is required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            comment_found = False
            for comment_entry in post.comments:
                if str(comment_entry['_id']) == comment_id:
                    comment_found = True
                    post.comments.remove(comment_entry)
                    break
            
            if not comment_found:
                return Response({'message': 'Comment not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            post.save()
            return Response({'message': 'Comment deleted successfully!'}, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CommentLikeView(APIView):
    def get(self, request, post_id, comment_id):
        try:
            user = authenticate_user(request)   
             
            post = Posts.objects.get(_id=post_id)
            
            if post is None:
                return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            if not comment_id:
                return Response({'message': 'Comment ID is required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not post.comments:
                return Response({'message': 'Comment not found!'}, status=status.HTTP_404_NOT_FOUND)         


            creator = User.objects.get(_id=post.orginal_creator_user_id)
            
            if creator is None:
                return Response({'message': 'Post creator not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            if creator._id != user._id and creator.is_locked and str(creator._id) not in user.connected_user_ids:
                return Response({'message': 'This post is from locked profile.'}, status=status.HTTP_403_FORBIDDEN)              
            
                
            comment_found = False
            for comment_entry in post.comments:
                if str(comment_entry['_id']) == comment_id:
                    comment_found = True
                    
                    for comment_like in comment_entry['comment_likes']:
                        if comment_like['user_id'] == user._id:
                            comment_entry['comment_likes'].remove(comment_like)
                            post.save()
                            return Response({'message': 'Comment unliked successfully!'}, status=status.HTTP_200_OK)
                    break
            
            if not comment_found:
                return Response({'message': 'Comment not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            for comment_entry in post.comments:
                if str(comment_entry['_id']) == comment_id:
                    comment_entry['comment_likes'].append({
                        'user_id': user._id,
                        'datetime': timezone.now()
                    })
                    post.save()
                    return Response({'message': 'Comment liked successfully!'}, status=status.HTTP_200_OK)
            
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CommentAllView(APIView):
    def get(self, request, post_id):
        try:
            user = authenticate_user(request)   
                        
            post = Posts.objects.get(_id=post_id)
            
            if post is None:
                return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)

            if post is None:
                return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
            

            creator = User.objects.get(_id=post.orginal_creator_user_id)
            
            if creator is None:
                return Response({'message': 'Post creator not found!'}, status=status.HTTP_404_NOT_FOUND)
            
            if creator._id != user._id and creator.is_locked and str(creator._id) not in user.connected_user_ids:
                return Response({'message': 'This post is from locked profile.'}, status=status.HTTP_403_FORBIDDEN)  
                        
            comments = post.comments
            
            formatted_comments = []
            
            for comment in comments:
                formatted_comments.append({
                    '_id': comment['_id'],
                    'comment': comment['comment'],
                    'comment_by_name': User.objects.get(_id=comment['comment_by']).name,
                    'comment_by_profile_pic': User.objects.get(_id=comment['comment_by']).profile.get('profile_picture'),
                    'comment_likes': len(comment['comment_likes']),
                    'datetime': comment['datetime']
                })
                
            page = request.GET.get('page')
            size = request.GET.get('size')
            
            
            formatted_data = []

            
            if (page is None and size is not None) or (page is not None and size is None):
                return Response({'message': 'Invalid query parameters. If  you can not  set  only either page  or  size parameter. You need  to set up  both or  none of both.'}, status=status.HTTP_400_BAD_REQUEST)

            page = int(page) if page is not None and page.isdigit() else 1
            size = int(size) if size is not None and size.isdigit() else None    
            
            
            if size:
                paginator = Paginator(formatted_comments, size)
                try:
                    formatted_comments = paginator.page(page)
                except EmptyPage:
                    return Response([])

                total_elements = paginator.count
                total_pages = paginator.num_pages
                has_next = formatted_comments.has_next()
                has_previous = formatted_comments.has_previous

                formatted_data = list(formatted_comments)  # Convert Page to a list

                response_data = {
                    'data': formatted_data,
                    'first_page': 1,
                    'next_page': page + 1 if has_next else None,
                    'total_elements': total_elements,
                    'last_page': total_pages
                }

            if not size:
                response_data = {
                    'data': formatted_comments,
                    'first_page': 1,
                    'next_page': None,
                    'total_elements': len(formatted_comments),
                    'last_page': None
                }
                
            return Response(response_data, status=status.HTTP_200_OK)    
        
        except AuthenticationFailed as e:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
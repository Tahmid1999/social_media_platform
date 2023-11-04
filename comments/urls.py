from django.urls import path, include
from .views import CreateCommentView, CommentUpdateView, CommentDeleteView, CommentLikeView, CommentAllView

urlpatterns = [
    path('create/<str:post_id>', CreateCommentView.as_view()),
    path('update/<str:post_id>/<str:comment_id>', CommentUpdateView.as_view()),
    path('delete/<str:post_id>/<str:comment_id>', CommentDeleteView.as_view()),
    path('like/<str:post_id>/<str:comment_id>', CommentLikeView.as_view()),
    path('all/<str:post_id>', CommentAllView.as_view()),
    
]
from django.urls import path, include
from .views import LikePostView, AllLikesView


urlpatterns = [
    path('<str:post_id>', LikePostView.as_view()),
    path('all/<str:post_id>', AllLikesView.as_view()),
]
from django.urls import path, include
from .views import CreateSharedPostView


urlpatterns = [
    path('<str:post_id>', CreateSharedPostView.as_view()),    
]
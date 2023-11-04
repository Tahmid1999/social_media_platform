from django.urls import path, include
from .views import UserProfileView,OtherUserProfileView



urlpatterns = [
    path('details', UserProfileView.as_view()),
    path('details/<str:user_id>', OtherUserProfileView.as_view()),
]

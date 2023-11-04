from django.urls import path, include
from .views import FeedShowView

urlpatterns = [
    path('view', FeedShowView.as_view()),
]
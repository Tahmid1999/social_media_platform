from django.urls import path, include
from .views import PostCreateView, PostUpdateView, PostDeleteView, PostByIdView, SelfAllPostView, SearchByKeywordView, OtherAllPostView

urlpatterns = [
    path('create', PostCreateView.as_view()),
    path('update/<str:post_id>', PostUpdateView.as_view()),
    path('delete/<str:post_id>', PostDeleteView.as_view()),
    path('view/<str:post_id>', PostByIdView.as_view()),
    path('all', SelfAllPostView.as_view()),
    path('all/<str:user_id>', OtherAllPostView.as_view()),
    path('search/<str:keyword>', SearchByKeywordView.as_view()),
    path('likes/', include('likes.urls')),
    path('comments/', include('comments.urls')),
    path('shares/', include('sharepost.urls'))
    
]
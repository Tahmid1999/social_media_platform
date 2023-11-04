from django.urls import path, include
from .views import RegisterView, VerifyEmailView,  LoginView, UserView, PasswordUpdateView, UserListView, UserSearchView, UserLockView, CheckEmailExsistOrNotView, PassResetOtpCheckView, PassResetView 

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('verify-email', VerifyEmailView.as_view()),
    
    path('check-email-exists', CheckEmailExsistOrNotView.as_view()),
    path('check-passwors-reset-otp', PassResetOtpCheckView.as_view()),
    path('password-reset',  PassResetView.as_view()),
    
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),    
    path('all_users', UserListView.as_view()),
    path('user_search', UserSearchView.as_view()),
    path('password-update', PasswordUpdateView.as_view()),
    path('lock-user', UserLockView.as_view()),
    path('connections/', include('connections.urls')),
    path('feed/', include('feed.urls'))
]



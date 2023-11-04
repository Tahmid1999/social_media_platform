from django.urls import path, include
from .views import SendRequestView, AcceptRequestView, CancleRequestView, AllConnectionsView, AllConnectionsByNameView

urlpatterns = [
    path('request/<str:user_id>', SendRequestView.as_view()),
    path('accept/<str:connection_id>', AcceptRequestView.as_view()),
    path('cancle/<str:connection_id>', CancleRequestView.as_view()),
    path('all', AllConnectionsView.as_view()),
    path('all/<str:user_name>', AllConnectionsByNameView.as_view())
    # path('verify-email', VerifyEmailView.as_view()),
    # path('login', LoginView.as_view()),
    # path('user', UserView.as_view()),
    # path('all_users', UserListView.as_view()),
    # path('user_search', UserSearchView.as_view()),
    # path('password-update', PasswordUpdateView.as_view(), name='password-update'),
    # path('connections/', include('connections.urls'))
]


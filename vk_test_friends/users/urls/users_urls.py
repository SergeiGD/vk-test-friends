from django.urls import path

from users.views import UsersListAPIView, UserAPIView


urlpatterns = [
    path('', UsersListAPIView.as_view(), name='users_list'),
    path('<int:pk>/', UserAPIView.as_view(), name='user'),
]

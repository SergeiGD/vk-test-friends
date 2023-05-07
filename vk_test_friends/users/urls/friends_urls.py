from django.urls import path

from users.views import (
    FiendsListAPIView, FriendAPIView, friendship_status_api_view
)


urlpatterns = [
    path('', FiendsListAPIView.as_view(), name='friends_list'),
    path('<int:pk>/', FriendAPIView.as_view(), name='friend'),
    path('<int:pk>/status/', friendship_status_api_view, name='friendship_status'),
]

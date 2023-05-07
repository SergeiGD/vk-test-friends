from django.urls import path

from friend_requests.views import (
    IncomingRequestsListAPiView, OutcomingRequestsListAPiView, OutcomingRequestAPiView, IncomingRequestAPiView,
    reject_request_api_view, confirm_request_api_view,
)


urlpatterns = [
    path('incoming_requests/', IncomingRequestsListAPiView.as_view(), name='incoming_requests_list'),
    path('incoming_requests/<int:pk>/', IncomingRequestAPiView.as_view(), name='incoming_request'),
    path('incoming_requests/<int:pk>/confirm/', confirm_request_api_view, name='confirm_request'),
    path('incoming_requests/<int:pk>/reject/', reject_request_api_view, name='reject_request'),
    path('outcoming_requests/', OutcomingRequestsListAPiView.as_view(), name='outcoming_requests_list'),
    path('outcoming_requests/<int:pk>/', OutcomingRequestAPiView.as_view(), name='outcoming_request'),
]

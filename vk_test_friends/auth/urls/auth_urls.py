from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth.views import SingUpView, VerifyAccountAPIView, RequestResetPasswordAPIView, ConfirmResetPasswordAPIView


urlpatterns = [
    path('sing_up/', SingUpView.as_view(), name='sing_up'),
    path('sing_up/verify_account/', VerifyAccountAPIView.as_view(), name='verify_account'),
    path('reset_password/', RequestResetPasswordAPIView.as_view(), name='request_reset_password'),
    path('reset_password/confirm_reset/', ConfirmResetPasswordAPIView.as_view(), name='confirm_reset_password'),
    path('tokens/', TokenObtainPairView.as_view(), name='token_get_pair'),
    path('tokens/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

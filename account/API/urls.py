from django.urls import path
from account.API.views import AuthUserAPIView, LoginPasswordAPIView, \
    SignUpUserAPIView, VerifyOTPAPIView

app_name = 'account'

urlpatterns = [
    path('user/', AuthUserAPIView.as_view(), name='auth-user'),
    path('login/', LoginPasswordAPIView.as_view(), name='login'),
    path('otp-code/', VerifyOTPAPIView.as_view(), name='otp-code'),
    path('signup/', SignUpUserAPIView.as_view(), name='signup'),
]
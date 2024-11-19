import redis
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.API.serializers import SignUpUserSerializer, AuthUserSerializer, \
    LoginPasswordSerializer, VerifyOTPSerializer
from account.models import User
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
BLOCK_DURATION = 3600


class AuthUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AuthUserSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data,
                            status=status.HTTP_200_OK if 'next_endpoint' in response_data and
                                                         response_data[
                                                             'next_endpoint'] == '/auth/login/' else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        username = request.data.get('username')
        login_attempt_key = f'login_attempts:{username}:{ip_address}'
        blocked_key = f'blocked:{username}:{ip_address}'

        if redis_client.exists(blocked_key):
            return Response({
                'message': 'Your account is temporarily blocked. Please try again later.'},
                status=status.HTTP_403_FORBIDDEN)

        serializer = LoginPasswordSerializer(data=request.data,
                                             user=request.user)
        if serializer.is_valid():
            response_data = serializer.save()
            redis_client.delete(login_attempt_key)
            return Response(response_data, status=status.HTTP_200_OK)

        attempts = redis_client.incr(login_attempt_key)
        if attempts == 1:
            redis_client.expire(login_attempt_key, BLOCK_DURATION)

        if attempts >= 3:
            redis_client.setex(blocked_key, BLOCK_DURATION, 'blocked')
            return Response({
                'message': 'Too many incorrect login attempts. You are blocked for 1 hour.'},
                status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAPIView(APIView):
    def post(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        phone_number = request.data.get('phone_number')
        otp_attempt_key = f'otp_attempts:{phone_number}:{ip_address}'
        blocked_key = f'otp_blocked:{phone_number}:{ip_address}'

        if redis_client.exists(blocked_key):
            return Response({
                'message': 'You are temporarily blocked. Please try again later.'},
                status=status.HTTP_403_FORBIDDEN)

        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            redis_client.delete(otp_attempt_key)
            return Response(response_data, status=status.HTTP_200_OK)

        attempts = redis_client.incr(otp_attempt_key)
        if attempts == 1:
            redis_client.expire(otp_attempt_key, BLOCK_DURATION)

        if attempts >= 3:
            redis_client.setex(blocked_key, BLOCK_DURATION, 'blocked')
            return Response({
                'message': 'Too many incorrect OTP submissions. You are blocked for 1 hour.'},
                status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        phone_number = user.phone_number

        try:
            user = User.objects.get(phone_number=phone_number)
            serializer = SignUpUserSerializer(user, data=request.data,
                                              partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'message': 'User information updated successfully.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'message': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

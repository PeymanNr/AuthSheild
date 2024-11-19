import random
import jwt
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import User
from config.local_settings import SECRET_KEY


class SignUpUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'password',
                  'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class AuthUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, data):
        phone_number = data.get('phone_number')
        if not phone_number:
            raise serializers.ValidationError(
                {'message': 'Phone number is required'})

        return data

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        try:
            user = User.objects.get(phone_number=phone_number)
            refresh = RefreshToken.for_user(user)
            return {
                'message': f'Hi {user.first_name}. Please enter your password.',
                'next_endpoint': reverse('account:login'),
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

        except User.DoesNotExist:
            user = User.objects.create(phone_number=phone_number)
            refresh = RefreshToken.for_user(user)
            otp_code = random.randint(100000, 999999)

            payload = {
                'otp_code': otp_code
            }

            otp_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            return {
                'message': 'Wellcome',
                'next_endpoint':reverse('account:otp-code'),
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'otp_token': otp_token,
                'otp_code': otp_code
            }


class LoginPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        password = data.get('password')

        if not self.user:
            raise serializers.ValidationError(
                {'message': 'User is not authenticated'})

        if not self.user.check_password(password):
            raise serializers.ValidationError({'message': 'Invalid password'})

        return data

    def create(self, validated_data):
        return {
            'message': 'Login successful',
            'user': {
                'phone_number': self.user.phone_number
            }
        }


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField()
    otp_token = serializers.CharField()

    def validate(self, data):
        otp_code = data.get('otp_code')
        otp_token = data.get('otp_token')

        if not otp_token or not otp_code:
            raise serializers.ValidationError(
                {'message': 'OTP token or OTP code is required'})

        try:
            decoded_payload = jwt.decode(otp_token, SECRET_KEY,
                                         algorithms=['HS256'])
            stored_otp_code = decoded_payload['otp_code']

            if otp_code != str(stored_otp_code):
                raise serializers.ValidationError({'message': 'Invalid OTP'})

        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError(
                {'message': 'OTP token has expired'})
        except jwt.DecodeError:
            raise serializers.ValidationError({'message': 'Invalid OTP token'})

        return data

    def create(self, validated_data):

        return {
            'message': 'OTP validated successfully.',
            'next_endpoint': reverse('account:signup')
        }

from django.shortcuts import render

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response

from django.contrib.auth.models import User, Group
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings

from .serializers import UserSerializer, InstituteUserSerializer, ResetPasswordSerializer, ChangePasswordSerializer
from user_profiles.user_group_models import InstituteProfile

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # bug may occur in case of multiple groups
        group = user.groups.first()
        token['group'] = str(group)
        token['username'] = user.username

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserCreateAPIView(generics.CreateAPIView):
    """
    for accounts for test attending candidates
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if not serializer.is_valid():
            return Response({'detail': 'Account already registered with the same email'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class ForgotPasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        print(email)
        if email:
            try :
                user = User.objects.get(email = email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = self.reset_url(request, uid, token)
                self.send_reset_email(user.email, reset_url)
                return Response({'detail': 'Password reset email sent'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                pass
        return Response({'detail': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
    
    def reset_url(self, request, uid, token):
        current_site = get_current_site(request)
        print(request.scheme, current_site.domain, "inside forgot password")
        return f"{request.scheme}://{current_site.domain}/reset-password/{uid}/{token}/"
    
    def send_reset_email(self, email, reset_url):
        subject = 'Password Reset'
        message = f'Use the following link to reset your password: {reset_url}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

class RestPasswordAPIView(APIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, uidb64, token):
        data = request.data
        serializer = self.get_serializer(data = data)
        if serializer.is_valid():
            try :
                uidb64 = serializer.validated_data['uidb64']
                token = serializer.validated_data['token']
                new_password = serializer.validated_data['new_password']
                
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                pass
        return Response({'detail': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAPIView(APIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data = data)
        try:
            if serializer.is_valid():
                user = request.user
                old_password = serializer.validated_data['old_password']
                new_password = serializer.validated_data['new_password']
                if not user.check_password(old_password):
                    return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
                # Set the new password and save it
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstituteUserCreateAPIView(generics.CreateAPIView):
    serializer_class = InstituteUserSerializer




    

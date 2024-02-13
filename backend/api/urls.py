from django.urls import path

from .views import MyTokenObtainPairView, UserCreateAPIView, InstituteUserCreateAPIView, RestPasswordAPIView, ForgotPasswordAPIView, ChangePasswordAPIView


from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)


urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('create_user/', UserCreateAPIView.as_view(), name = 'create_user'),
    path('create_institute_user/', InstituteUserCreateAPIView.as_view(), name = 'create_institute_user'),
    path('forgot_password/', ForgotPasswordAPIView.as_view(), name = 'forgot_password'),
    path('reset_password/', RestPasswordAPIView.as_view(), name = 'reset_password'),
    path('change_password/', ChangePasswordAPIView.as_view())

]
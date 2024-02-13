from django.contrib.auth.models import User, Group

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user_profiles.models import Profile
from user_profiles.user_group_models import InstituteProfile

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password'
        ]
        extra_kwargs = {
            'password':{
                'write_only': True
            }
        }

    def create(self, validated_data):
        print(validated_data)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        group , created= Group.objects.get_or_create(name = 'student')
        user.groups.add(group)
        Profile.objects.create(
            user = user,
            name = user.username,
            email  = user.email,
        )
        return user
    
class InstituteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password'
        ]
        extra_kwargs = {
            'password':{
                'write_only': True
            }
        }
    # make the fr form change the fiels then the radio button is set to institute and take these fields in the beginning
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        group, created= Group.objects.get_or_create(name = 'institute')
        user.groups.add(group)
        institute_profile =  InstituteProfile.objects.create(
                user = user,
                college_name = "default field",
                email = user.email,
                phone = 123123123,
                university_name = "default field",
                address = "default field"
            )
        return {
                    "email": user.email,
                    "username": user.username,
                    "phone":  "not set",
                    "college_name": "not set",
                    "university_name": 'not set',
                    "address": "set these later",
                    }
    
class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
        
# class InstituteUserSerializer(serializers.Serializer):
#     """
#     to create the login_id for an institute
#     """
    
#     email = serializers.EmailField()
#     username = serializers.CharField()
#     phone = serializers.IntegerField()
#     college_name = serializers.CharField()
#     university_name = serializers.CharField()
#     address =serializers.CharField()
#     password = serializers.CharField(write_only = True)

#     def create(self, validated_data):
#         # creating Institute profile user 
#         password = validated_data.pop('password')
#         college_name = validated_data.pop('college_name')
#         university_name = validated_data.pop('university_name')
#         address  = validated_data.pop('address')
#         phone  = validated_data.pop('phone')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()

#         group= Group.objects.get(name = 'institute')
#         print(group)
#         user.groups.add(group)
#         institute_profile =  InstituteProfile.objects.create(
#                 user = user,
#                 college_name = college_name,
#                 email = user.email,
#                 phone = phone,
#                 university_name = university_name,
#                 address = address

#             )
#         # this return value is given as output after a user is created
#         return {
#             "email": user.email,
#             "username": user.username,
#             "phone": phone,
#             "college_name": college_name,
#             "university_name": university_name,
#             "address": address,
#             }

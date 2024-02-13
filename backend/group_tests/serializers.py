from rest_framework import serializers

from .models import (GroupTest, GroupTestCategory, GroupTestCombinedCategory,
                     SubTestSessionPassword, GroupTestPassword, CategoryTestSession, CategorySessionPassword, 
                    CombinedCategoryTestSession, CombinedCategorySessionPassword, SubTestSession
)
                     
class GroupTestSerializer(serializers.ModelSerializer):
    # for creating of group test
    class Meta:
        model = GroupTest
        fields = [
            'pk',
            'name',
            'description',
            'category',
            'easy_test_file',
            'medium_test_file',
            'hard_test_file',
]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupTestCategory
        fields = [
            'pk',
            'name'
        ]


class CombinedCategorySerializer(serializers.ModelSerializer):
    associated_categories  = CategorySerializer(many = True, read_only=True)
    
    class Meta:
        model = GroupTestCombinedCategory
        fields = [
            'pk',
            'name',
            'associated_categories',
        ]


class SubTestPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTestSessionPassword
        fields = [
            'session',
            'password'
        ]

        extra_kwargs = {
            'password' : {'write_only'  :True}
        }

class SubTestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTestSession
        fields = [
            'pk',
            'name',
            'has_password',
            'start_time',
            'end_time',
            'sub_test',
            'duration',
        ]


class CategoryTestSessionSerializer(serializers.ModelSerializer):
    """
    for creating test sessions based on the category
    """
    class Meta:
        model = CategoryTestSession
        fields = [
            'pk',
            'name',
            'has_password',
            'start_time',
            'end_time',
            'category',
            'duration',
        ]

class CombinedCategoryTestSessionSerializer(serializers.ModelSerializer):
    """
    for creating test sessions based on the category
    """
    class Meta:
        model = CombinedCategoryTestSession
        fields = [
            'pk',
            'name',
            'has_password',
            'start_time',
            'end_time',
            'combined_category',
            'duration',
        ]
        

class CategoryPasswordSerializer(serializers.ModelSerializer):
    """
    saves passowrds for CategegoryTestSessionSerializer
    """
    class Meta:
        model = CategorySessionPassword
        fields = [
            'session',
            'password'
        ]

        extra_kwargs = {
            'password' : {'write_only'  :True}
        }



class CombinedCategoryPasswordSerializer(serializers.ModelSerializer):
    """
    saves passowrds for CategegoryTestSessionSerializer
    """
    class Meta:
        model = CombinedCategorySessionPassword
        fields = [
            'session',
            'password'
        ]

        extra_kwargs = {
            'password' : {'write_only'  :True}
        }

class CategorySessionAuthenticationSerializer(serializers.Serializer):
    session_id  = serializers.IntegerField()
    unique_id = serializers.CharField(max_length = 20)
    password = serializers.CharField(max_length = 50)


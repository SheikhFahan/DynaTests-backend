from rest_framework import serializers

from .models import Profile, TestMarksLibrary
from .user_group_models import InstituteProfile

from tests.serializers import CategoryListCreateSerializer

import datetime

class StudentProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(read_only = True)
    class Meta:
        model = Profile
        fields = [
            'name',
            'phone',
            'email',
            'address',
            'password',
        ]

class InstituteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteProfile
        fields = [
            'college_name',
            'email',
            'phone',
            'university_name',
            'address',
        ]


class TestMarksLibraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestMarksLibrary
        fields = [
            'score',
            'timestamp',
        ]

class AttemptedCategoryCountsListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    category_name = serializers.CharField(max_length = 30)
    count = serializers.IntegerField()


class TestHistorySerializer(serializers.Serializer):
    category_name = serializers.CharField(max_length = 30)
    test_score = serializers.IntegerField()
    date = serializers.DateTimeField()

class QuestionsStatisticsSerializer(serializers.Serializer):
    total_questions = serializers.IntegerField()
    total_easy = serializers.IntegerField()
    total_medium = serializers.IntegerField()
    total_hard= serializers.IntegerField()
    solved_easy = serializers.IntegerField()
    solved_medium = serializers.IntegerField()
    solved_hard = serializers.IntegerField()


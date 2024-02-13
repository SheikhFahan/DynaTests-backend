from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import  TokenAuthentication

from django.http import JsonResponse
from django.db.models import Count, F

from tests.models import EasyQuestion, MediumQuestion, HardQuestion
from api.permissions import IsStudent, IsInstitute
from api.pagination import TestHistoryPagination

from .serializers import  (
                            StudentProfileSerializer, TestMarksLibraryListSerializer,
                            InstituteProfileSerializer, AttemptedCategoryCountsListSerializer, 
                            QuestionsStatisticsSerializer,TestHistorySerializer
                           )
from .models import TestMarksLibrary, Profile, QuestionStatistics, TestScoresLibrary
from .user_group_models import InstituteProfile

class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudent]

    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user = user)
        serializer = self.serializer_class(instance=profile, data=request.data, partial=True)
        if serializer.is_valid(): 
            password = serializer.validated_data.get('password')
            if password and  user.check_password(password):
                serializer.save()  # Save the updated profile
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_object(self):
        user = self.request.user
        profile = Profile.objects.get(user = user)
        return profile
    
    
class InstituteProfileRetrieveAPIView(generics.RetrieveAPIView):
    queryset = InstituteProfile.objects.all()
    serializer_class = InstituteProfileSerializer
    permission_classes = [IsInstitute]

    def get_object(self):
        print("coming here")
        user = self.request.user
        profile = InstituteProfile.objects.get(user = user)
        return profile
    


class UserAttemptedCategoriesDataAPIView(generics.ListAPIView):
    serializer_class = AttemptedCategoryCountsListSerializer

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.get(user = user)
        # gets the categories from the tests the user has attempted
        category_counts = TestMarksLibrary.objects.filter(profile = profile).values(category_name = F('category__name'), pk=F('category_id')).annotate(count=Count('category'))
        print(category_counts)
        return category_counts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
class TestHistoryListAPIView(generics.ListAPIView):
    serializer_class = TestHistorySerializer
    pagination_class = TestHistoryPagination

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.get(user = user)
        history = TestScoresLibrary.objects.filter(profile = profile).values(category_name = F('category__name'), date = F('timestamp'), test_score = F('score'))
        print(history)
        return history
    
class TestMarksLibraryListAPIView(generics.ListAPIView):
    serializer_class = TestMarksLibraryListSerializer

    def get_queryset(self):
        category = self.kwargs['category']
        user = self.request.user
        profile  = Profile.objects.get(user =user)
        marks_lib = TestMarksLibrary.objects.filter(profile = profile, category = category)
        return marks_lib
    
class QuestionStatisticsListAPIView(generics.ListAPIView):
    serializer_class  = QuestionsStatisticsSerializer

    def get_queryset(self):
        category = self.kwargs.get('category', False)
        # print(self.query_params())
        if category:
            statistics = QuestionStatistics.objects.get(user= self.request.user, category = category)
            solved_easy =  statistics.easy_count.count()
            solved_medium = statistics.medium_count.count()
            solved_hard = statistics.hard_count.count()
            print(solved_easy, solved_medium, solved_hard, "here ")
            total_easy = EasyQuestion.objects.filter(category = category).count()
            total_medium = MediumQuestion.objects.filter(category = category).count()
            total_hard = HardQuestion.objects.filter(category = category).count()
            print(total_easy, total_medium, total_hard)
        else:
            statistics_objects = QuestionStatistics.objects.filter(user= self.request.user)
            solved_easy, solved_medium, solved_hard = 0, 0, 0
            for obj in statistics_objects:
                solved_easy +=  obj.easy_count.count()
                solved_medium += obj.medium_count.count()
                solved_hard += obj.hard_count.count()
            total_easy = EasyQuestion.objects.all().count()
            total_medium = MediumQuestion.objects.all().count()
            total_hard = HardQuestion.objects.all().count()
        total_questions = total_easy + total_medium + total_hard
        queryset = {
            'total_questions' : total_questions,
            'total_easy' : total_easy ,
            'total_medium' : total_medium,
            'total_hard' : total_hard,
            'solved_easy' : solved_easy,
            'solved_medium' : solved_medium,
            'solved_hard' : solved_hard,
        }
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print(queryset, "queryset")
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from django.db.models import F, Count
from collections import defaultdict

from .visualization_api_serializer import (QuestionsDataSerializer, QuestionsDataDetailSerializer,
                                           CCDataSerializer, SessionScoresSerializer, SessionsListSerializer)
from .models import GroupTest, GroupTestCategory, GroupTestCombinedCategory
from .models import (
    SubTestsMarksLibrary, GroupTestMarksLibrary, CombinedGroupTestMarksLibrary,
    SubTestSession, CategoryTestSession, CombinedCategoryTestSession
)

from api.permissions import IsInstitute, IsInstituteAndOwner, IsStudent


class SubTestListAPIVIew(generics.ListAPIView):
    """
    gives the total number of subtests per category
    """
    serializer_class = QuestionsDataSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user  = self.request.user
        # can put an if block over here to for dry
        category_counts = GroupTest.objects.filter(user = user).values(category_name = F('category__name'), pk=F('category_id')).annotate(count=Count('category_name'))
        print(category_counts)
        return category_counts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
class SubTestDetailsListAPIView(generics.ListAPIView):
    """
        gives the total number of question per subtest according to the difficulty
    """
    serializer_class = QuestionsDataDetailSerializer
    # permission_classes = [IsInstitute]

    def get_queryset(self):
        user = self.request.user
        category_counts = GroupTest.objects.filter(user=user).values(test_name = F('name'),test_pk = F('pk'), category_name = F('category__name'), category_pk=F('category_id'))   
        for category_count in category_counts:
            group_test_instance = GroupTest.objects.get(pk=category_count['test_pk'])
            category_count['total_easy'] =group_test_instance.easy_question.count()
            category_count['total_medium'] = group_test_instance.medium_question.count()
            category_count['total_hard'] = group_test_instance.hard_question.count()
        return category_counts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
class GroupCategoryInfoListAPIVIew(generics.ListAPIView):
    """
    gives the total number of subtests per category
    """
    serializer_class = QuestionsDataSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user  = self.request.user
        # the pk might give errors because of the annotation problems
        category_counts = GroupTestCategory.objects.filter(user = 5).values(category_name = F('name'), pk=F('pk'))
        return category_counts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
class GroupCategoryDetailsListAPIView(generics.ListAPIView):
    """
        gives the total number of question per subtest according to the difficulty
    """
    serializer_class = QuestionsDataDetailSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user = self.request.user
        category_counts = GroupTestCategory.objects.filter(user=user) .values(category_name = F('name'),category_pk = F('pk'))   
        for category_count in category_counts:
            category_instance = GroupTestCategory.objects.get(pk=category_count['category_pk'])
            category_count['total_easy'] =category_instance.easy_question.count()
            category_count['total_medium'] = category_instance.medium_question.count()
            category_count['total_hard'] = category_instance.hard_question.count()
        return category_counts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

class CCInfoListAPIView(generics.ListAPIView):
    serializer_class = CCDataSerializer
    # permission_classes = [IsInstitute]
    def get_queryset(self):
        user  = self.request.user
        merged_results = defaultdict(list)
        queryset = GroupTestCombinedCategory.objects.filter(user = user).values(category_name = F('name'), pk=F('pk'), associated_categories_list=F('associated_categories__name'))
        for item in queryset:
            key = (item['category_name'], item['pk'])
            merged_results[key].append(item['associated_categories_list'])

        print(merged_results)
        merged_queryset = [
            {
                'category_name': key[0],
                'pk': key[1],
                'associated_categories_list': ', '.join(values)
            }
            for key, values in merged_results.items()
        ]
        return merged_queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    

class SubTestSessionsListAPIView(generics.ListAPIView):
    serializer_class = SessionsListSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        institute = self.request.user
        sessions = SubTestSession.objects.filter(user = institute)
        print(sessions)
        return  sessions
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
class GroupTestCategorySessionsListAPIView(generics.ListAPIView):
    serializer_class = SessionsListSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        institute = self.request.user
        sessions = CategoryTestSession.objects.filter(user = institute)
        print(sessions)
        return  sessions
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

class CCGroupTestSessionsListAPIView(generics.ListAPIView):
    serializer_class = SessionsListSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        institute = self.request.user
        sessions = CombinedCategoryTestSession.objects.filter(user = institute)
        print(sessions)
        return  sessions
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)



class SubTestSessionsDetailedDataListAPIView(generics.ListAPIView):
    serializer_class = SessionScoresSerializer
    permission_classes = [IsInstitute]
    
    def get_queryset(self):
        institute = self.request.user
        session = self.kwargs['session']
        queryset = SubTestsMarksLibrary.objects.filter(institute = institute, session = session).annotate(name=F('candidate__username')).values('name', 'score')
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

class GroupTestSessionsDetailedDataListAPIView(generics.ListAPIView):
    serializer_class = SessionScoresSerializer
    permission_classes = [IsInstitute]
    
    def get_queryset(self):
        institute = self.request.user
        session = self.kwargs['session']
        queryset = GroupTestMarksLibrary.objects.filter(institute = institute, session = session).annotate(name=F('candidate__username')).values('name', 'score')
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

class CCGroupTestSessionsDetailedDataListAPIView(generics.ListAPIView):
    serializer_class = SessionScoresSerializer
    permission_classes = [IsInstitute]
    
    def get_queryset(self):
        institute = self.request.user
        session = self.kwargs['session']
        queryset = CombinedGroupTestMarksLibrary.objects.filter(institute = institute, session = session).annotate(name=F('candidate__username')).values('name', 'score')
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView     
from rest_framework import permissions

from django.db.models import F, Count

from .visualization_api_serializer import QuestionsDataSerializer, QuestionsDataDetailSerializer
from .models import GroupTest, EasyQuestion, MediumQuestion,  HardQuestion 

from api.permissions import IsInstitute, IsInstituteAndOwner, IsStudent


class SubTestsListAPIVIew(generics.ListAPIView):
    """
    gives the total number of subtests per category
    """
    serializer_class = QuestionsDataSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user  = self.request.user
        # can put an if block over here to for dry
        temp =  GroupTest.objects.filter(user = user)
        category_counts = GroupTest.objects.filter(user = user).values(category_name = F('category__name'), pk=F('category_id')).annotate(count=Count('category'))
        print(temp, "temp")
        return category_counts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
class SubTestsDetailsListAPIView(generics.ListAPIView):
    """
        gives the total number of question per subtest according to the difficulty
    """
    serializer_class = QuestionsDataDetailSerializer
    # permission_classes = [IsInstitute]

    def get_queryset(self):
        user = self.request.data
        category_counts = GroupTest.objects.filter(user=5) .values(test_name = F('name'),test_pk = F('pk'), category_name = F('category__name'), category_pk=F('category_id'))   
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

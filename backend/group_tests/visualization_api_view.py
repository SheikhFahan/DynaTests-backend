from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView     
from rest_framework import permissions

from django.db.models import F, Count

from .visualization_api_serializer import QuestionsDataSerializer, QuestionsDataDetailSerializer
from .models import GroupTest

from api.permissions import IsInstitute, IsInstituteAndOwner, IsStudent


class SubTestsListAPIVIew(generics.ListAPIView):
    """
    gives the total number of subtests per category
    """
    serializer_class = QuestionsDataSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user  = self.request.user
        category_counts = GroupTest.objects.filter(user = user).values(category_name = F('category__name'), pk=F('category_id')).annotate(count=Count('category'))
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
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user = self.request.data
        category_counts = GroupTest.objects.filter(user=user) .values('category__name', 'category_id').annotate(
        easy_count=Count('easyquestion'),
        medium_count=Count('mediumquestion'),
        hard_count=Count('hardquestion')
    )
        return category_counts
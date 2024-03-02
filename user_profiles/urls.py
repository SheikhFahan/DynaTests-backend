from django.urls import path
from .views import (
    ProfileRetrieveUpdateAPIView , UserAttemptedCategoriesDataAPIView, TestMarksLibraryListAPIView, 
    QuestionStatisticsListAPIView, InstituteProfileRetrieveAPIView, TestHistoryListAPIView
    )
urlpatterns = [
    path('profile_student/', ProfileRetrieveUpdateAPIView.as_view() ),
    path('profile_institute/', InstituteProfileRetrieveAPIView.as_view() ),
    path('categories/', UserAttemptedCategoriesDataAPIView.as_view() ),
    path('<int:category>/marks/', TestMarksLibraryListAPIView.as_view() ),
    path('questions_statistics/', QuestionStatisticsListAPIView.as_view() ),
    path('questions_statistics/<int:category>/', QuestionStatisticsListAPIView.as_view() ),
    path('history/', TestHistoryListAPIView.as_view() ),

]
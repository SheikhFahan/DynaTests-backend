from django.urls import path
from .views import (
    CategoriesListCreateAPIView, QuestionsRetrieveAPIView,
    SubmitAnswersAPIView, CCListCreateAPIView,
    CombinationTestQuestionsListAPIView,
    SubmitCombinationAnswersAPIView, QuestionsCreateAPIView
    )
urlpatterns = [
    path('categories/',CategoriesListCreateAPIView.as_view() ),
    path('combination_c/', CCListCreateAPIView.as_view() ),
    path('upload_questions/', QuestionsCreateAPIView.as_view()),
    path('<int:category>/get_comb_test/',CombinationTestQuestionsListAPIView.as_view()),
    path('<int:category>/get_test/',QuestionsRetrieveAPIView.as_view()),
    path('submit_ans/', SubmitAnswersAPIView.as_view() ),
    path('submit_comb_ans/', SubmitCombinationAnswersAPIView.as_view() ),

    # path()


]
from django.urls import path, include

from .views import (
    GroupTestListCreateAPIView, QuestionsRetrieveAPIView, 
    SubmitAnswersAPIView, GroupTestCategoryListCreateAPIView, PasswordCreateAPIView, 
    GroupTestCombinedCategoryListCreateAPIView, CategoryTestSessionListCreateAPIView,
    CombinedCategoryPasswordCreateAPIView, CombinedCategoryTestSessionListCreateAPIView,
    CategoryPasswordCreateAPIView, CategoryTestSessionQuestionsListAPIView, CombinationCategoryTestSessionQuestionsListAPIView,
    CategorySessionRetrieveAPIView, CategorySessionAuthentication, CombinedCategorySessionRetrieveAPIView,
    CombinedCategorySessionAuthentication, SubmitCombinationAnswersAPIView, SubTestSessionListCreateAPIView,
    SubTestSessionAuthentication, SubTestSessionRetrieveAPIView, SubTestSessionQuestionsListAPIView,
    SubTestAnswerSubmitAPIView 
)

from .visualization_api_view import (
    SubTestListAPIVIew, SubTestDetailsListAPIView,GroupCategoryInfoListAPIVIew,
    GroupCategoryDetailsListAPIView, CCInfoListAPIView
)

urlpatterns = [
    # for creating and listing group tests and categories for the tests
    path('group_test_combined_categories/', GroupTestCombinedCategoryListCreateAPIView.as_view()),
    path('group_test_categories/', GroupTestCategoryListCreateAPIView.as_view()),
    path('group_sub_test/', GroupTestListCreateAPIView.as_view()),

    # creating and listing  test sessions
    # add pagination for fetch 
    path('session_by_subtest/', SubTestSessionListCreateAPIView.as_view()),
    path('session_by_category/', CategoryTestSessionListCreateAPIView.as_view()),
    path('session_by_combined_category/', CombinedCategoryTestSessionListCreateAPIView.as_view()),
    # create password for sessions
    path('create_subtest_session_passwords/', PasswordCreateAPIView.as_view()),
    path('create_category_session_passwords/', CategoryPasswordCreateAPIView.as_view()),
    path('create_combined_category_session_passwords/', CombinedCategoryPasswordCreateAPIView.as_view()),
    # fetch sessions questions
    path('subtest_session/<int:inst>/<int:session_id>/', SubTestSessionQuestionsListAPIView.as_view()),
    path('category_test_session/<int:inst>/<int:session_id>/', CategoryTestSessionQuestionsListAPIView.as_view()),
    path('combined_category_test_session/<int:inst>/<int:session_id>/', CombinationCategoryTestSessionQuestionsListAPIView.as_view()),
    # submitting answers
    path('submit_ans_subtest/', SubTestAnswerSubmitAPIView.as_view()),
    path('submit_ans_c/', SubmitAnswersAPIView.as_view()),
    path('submit_ans_cc/', SubmitCombinationAnswersAPIView.as_view()),
    # fetch sessions data user_id -> institute_id
    path('session_subtest_data/<int:user_id>/<int:pk>/', SubTestSessionRetrieveAPIView.as_view()),
    path('session_category_data/<int:user_id>/<int:pk>/', CategorySessionRetrieveAPIView.as_view()),
    path('session_combined_category_data/<int:user_id>/<int:pk>/', CombinedCategorySessionRetrieveAPIView.as_view()),

    # check  password for the sessions -> might add inst_id later if the data grows a lot
    path('authenticate_session_subtest/', SubTestSessionAuthentication.as_view()),
    path('authenticate_session_c/', CategorySessionAuthentication.as_view()),
    path('authenticate_session_cc/', CombinedCategorySessionAuthentication.as_view()),

    # path('sub_group_test/', GroupTestListCreateAPIView.as_view()),
    path('<int:category>/get_test/',QuestionsRetrieveAPIView.as_view()), 
    path('submit_ans/', SubmitAnswersAPIView.as_view() ),
    # db details for questions and categories
    path('subtest_data/', SubTestListAPIVIew.as_view() ),
    path('subtest_detailed_data/', SubTestDetailsListAPIView.as_view() ),

    path('category_test_data/', GroupCategoryInfoListAPIVIew.as_view() ),
    path('category_test_detailed_data/', GroupCategoryDetailsListAPIView.as_view() ),

    path('comprehensive_test_data/', CCInfoListAPIView.as_view() ),



]
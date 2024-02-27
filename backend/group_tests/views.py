# from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta, timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView     
from rest_framework import permissions

from api.permissions import IsInstitute, IsInstituteAndOwner, IsStudent

from . import visualization_api_view

from .serializers import (
    GroupTestSerializer, CategorySerializer, 
    SubTestPasswordSerializer, CombinedCategorySerializer,
    CategoryTestSessionSerializer, CategoryPasswordSerializer ,
    CombinedCategoryPasswordSerializer,
    CombinedCategoryTestSessionSerializer, SubTestSessionSerializer,
    CategorySessionAuthenticationSerializer
)
from .tasks import add_subtest_session_summary, add_category_test_session_summary, add_cc_session_summary

from .models import (GroupTest, GroupTestCombinedCategory, CategoryTestSession,
                    CombinedCategoryTestSession, CategorySessionPassword, 
                    CombinedCategorySessionPassword,GroupTestMarksLibrary,
                    CombinedGroupTestMarksLibrary
                    )

from .models import (
    GroupTestCategory, EasyQuestion, MediumQuestion, HardQuestion,
    ChoiceForEasyQ, ChoiceForHardQ, ChoiceForMediumQ, SubTestSessionPassword,
    SubTestSession, CombinedGroupTestMarksLibrary, GroupTestMarksLibrary, SubTestsMarksLibrary
)

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from user_profiles.models import Profile
from user_profiles.user_group_models import (GroupTestAverageScore,
                                             GroupTestScoresLibrary,  AttendanceCategorySession,
                                             AttendanceCCSession, AttendanceSubTest, )
from tests.serializers import QuestionSerializer, SubmitAnswersSerializer,  CombinedCategoryQuestionSerializer


class GroupTestCategoryListCreateAPIView(generics.ListCreateAPIView):
    #in the list method allow add isOwner rights 
    serializer_class = CategorySerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        user = self.request.user
        queryset = GroupTestCategory.objects.filter(user =user)
        return queryset

    def perform_create(self, serializer):
        print(serializer)
        name = self.request.data.get('name', "")
        serializer.save(user = self.request.user)
        
        return Response({'message': f'{name} Object created successfully'}, status=status.HTTP_201_CREATED)
    

class CategoryTestSessionListCreateAPIView(generics.ListCreateAPIView):
    """
    creates test session based on group test categories 
    """
    serializer_class = CategoryTestSessionSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        # to send the sessions that belong to the user 
        user = self.request.user
        queryset = CategoryTestSession.objects.filter(user =user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        data = request.data
        institute  = request.user
        serializer = self.get_serializer(data = data)
        if serializer.is_valid():
            session_object = serializer.save(user =institute)
            endtime = serializer.validated_data['end_time']
            add_category_test_session_summary.apply_async(kwargs={'session': session_object.pk, 'institute': institute.pk}, eta=endtime)

            # Include the 'pk' of the created object in the response incase password in needed to be saved
            response_data = {
                'pk': session_object.pk,
                'message': 'session created successfully.',
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CombinedCategoryTestSessionListCreateAPIView(generics.ListCreateAPIView):
    """
    create and list test SESSIONS as per combined category
    """
    serializer_class = CombinedCategoryTestSessionSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        # to send the sessions that belong to the user 
        user = self.request.user
        queryset = CombinedCategoryTestSession.objects.filter(user =user)
        return queryset

    def create(self, request, *args, **kwargs):
        # optimization -> get pk from the user
        data = request.data
        institute = request.user
        combined_category = data.pop('category')
        data['combined_category'] = combined_category
        serializer = self.get_serializer(data  =  data)
        if serializer.is_valid():
            session_object = serializer.save(user=institute)
            endtime = serializer.validated_data['end_time']
            add_cc_session_summary.apply_async(kwargs={'session': session_object.pk, 'institute': institute.pk}, eta=endtime)

            # Include the 'pk' of the created object in the response incase password in needed to be saved
            response_data = {
                'pk': session_object.pk,
                'message': 'session created successfully.',
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubTestSessionListCreateAPIView(generics.ListCreateAPIView):
    """
    create and list sub_tests
    """
    serializer_class = SubTestSessionSerializer
    permission_classes = [IsInstitute]

    def get_queryset(self):
        # to send the sessions that belong to the user 
        user = self.request.user
        queryset = SubTestSession.objects.filter(user =user)
        return queryset

    def create(self, request, *args, **kwargs):
        # optimization -> get pk from the user
        data = request.data
        print(data)
        sub_test = data.pop('category')
        data['sub_test'] = sub_test
        institute = request.user
        
        serializer = self.get_serializer(data  =  data)
        if serializer.is_valid():
            session_object = serializer.save(user=institute)
            endtime = serializer.validated_data['end_time']
            add_subtest_session_summary.apply_async(kwargs={'session': session_object.pk, 'institute': institute.pk}, eta=endtime)
            # Include the 'pk' of the created object in the response incase password in needed to be saved
            response_data = {
                'pk': session_object.pk,
                'message': 'session created successfully.',
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubTestSessionRetrieveAPIView(generics.RetrieveAPIView):
    """
    checks if the session,  user is looking for actually exists and send data about that
    """
    serializer_class = SubTestSessionSerializer
    queryset = SubTestSession.objects.all()
    lookup_fields = ['pk', 'user_id']

    def get_object(self):
        # return no session found if the there ain't one instead of the error
        queryset  = self.get_queryset()
        lookup_url_kwargs = {}
        for field in self.lookup_fields:
            lookup_url_kwargs[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **lookup_url_kwargs)
        # self.check_object_permissions(self.request, obj)
        return obj

class CategorySessionRetrieveAPIView(generics.RetrieveAPIView):
    """
    checks if the session,  user is looking for actually exists and send data about that
    """
    serializer_class = CategoryTestSessionSerializer
    queryset = CategoryTestSession.objects.all()
    lookup_fields = ['pk', 'user_id']

    def get_object(self):
        queryset  = self.get_queryset()
        lookup_url_kwargs = {}
        for field in self.lookup_fields:
            lookup_url_kwargs[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **lookup_url_kwargs)
        # self.check_object_permissions(self.request, obj)
        return obj

class CombinedCategorySessionRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CombinedCategoryTestSessionSerializer
    queryset = CombinedCategoryTestSession.objects.all()
    lookup_fields = ['pk', 'user_id']

    def get_object(self):
        queryset  = self.get_queryset()
        lookup_url_kwargs = {}
        for field in self.lookup_fields:
            lookup_url_kwargs[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **lookup_url_kwargs)
        # self.check_object_permissions(self.request, obj)
        return obj


class GroupTestCombinedCategoryListCreateAPIView(generics.ListCreateAPIView):
    """
    create and list TESTS as per combined categories
    """
    #in the list method allow add isOwner rights 
    serializer_class = CombinedCategorySerializer
    permission_classes = [IsInstitute]
    
    def get_queryset(self):
        queryset  =   GroupTestCombinedCategory.objects.filter(user = self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        print(request.data)
        # making data fit the serializer
        associated_categories_data = data.pop('associated_categories', [])
        serializer = CombinedCategorySerializer(data=data)

        if serializer.is_valid():
            instance = serializer.save(user=self.request.user)

            # Get existing category instances and associate them with the instance
            existing_categories = GroupTestCategory.objects.filter(pk__in=associated_categories_data)
            instance.associated_categories.set(existing_categories)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GroupTestListCreateAPIView(generics.ListCreateAPIView):
    """
    creates sub group tests
    """
    serializer_class = GroupTestSerializer
    permission_classes = [IsInstitute]
    
    def get_queryset(self):
        user = self.request.user
        queryset = GroupTest.objects.filter(user = user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = GroupTestSerializer(data = data, context = {'request' : request})
        if serializer.is_valid():
            group_test_object = serializer.save(user=request.user)
            
            # Include the 'pk' of the created object in the response incase password in needed to be saved
            response_data = {
                'pk': group_test_object.pk,
                'message': 'Test created successfully.',
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordCreateAPIView(generics.CreateAPIView):
    #  make sure that only the test owner can create or change passwords
    """
    saves the password for the tests which have is_password == True
    """
    serializer_class = SubTestPasswordSerializer


    def create(self, request, *args, **kwargs):
        data = request.data
        session  = data['session']
        
        try:
            session_object = SubTestSession.objects.get(pk=session)
        except SubTestSession.DoesNotExist:
            return Response({"error": "Invalid category_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        if SubTestSessionPassword.objects.filter(session=session_object).exists():
            return Response({"error": "Password already exists for this test"}, status=status.HTTP_400_BAD_REQUEST)
        
        hashed_password = make_password(data["password"])
        print(session, hashed_password)
        serializer = self.get_serializer(data = {'session' : session_object.pk, 'password' : hashed_password})
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryPasswordCreateAPIView(generics.CreateAPIView):
    #  make sure that only the test owner can create or change passwords
    # saves the password for the tests which have is_password == True
    serializer_class = CategoryPasswordSerializer


    def create(self, request, *args, **kwargs):
        data = request.data
        print(request.data)
        session  = data['session']
        
        try:
            session_object = CategoryTestSession.objects.get(pk= session)
        except CategoryTestSession.DoesNotExist:
            return Response({"error": "Invalid category_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        if CategorySessionPassword.objects.filter(session=session_object).exists():
            return Response({"error": "Password already exists for this test"}, status=status.HTTP_400_BAD_REQUEST)
        
        hashed_password = make_password(data["password"])
        print(session, hashed_password)
        serializer = self.get_serializer(data = {'session' : session_object.pk, 'password' : hashed_password})
        if serializer.is_valid():
            print("valid serializer")
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(status=status.HTTP_201_CREATED, headers=headers)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CombinedCategoryPasswordCreateAPIView(generics.CreateAPIView):
    #  make sure that only the test owner can create or change passwords
    # saves the password for the tests which have is_password == True
    serializer_class = CombinedCategoryPasswordSerializer


    def create(self, request, *args, **kwargs):
        data = request.data
        session  = data['session']
        print("coming here")
        try:
            print("coming above")
            session_object = CombinedCategoryTestSession.objects.get(pk=session)
            print("coming below")

        except CombinedCategoryTestSession.DoesNotExist:
            return Response({"error": "Invalid category_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        if CombinedCategorySessionPassword.objects.filter(session=session_object).exists():
            return Response({"error": "Password already exists for this test"}, status=status.HTTP_400_BAD_REQUEST)
        
        hashed_password = make_password(data["password"])
        print(session, hashed_password)
        serializer = self.get_serializer(data = {'session' : session_object.pk, 'password' : hashed_password})
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class SubTestSessionAuthentication(APIView):
    """
    to authenticate user for a session test -> can also be used to take the attendace in future  
    """

    # use acid properties for saving marking up attendance and allowing the test to the use 
    def post(self, request, *args, **kwargs):
        serializer = CategorySessionAuthenticationSerializer(data = request.data)
        print(serializer)
        if serializer.is_valid():
            unique_id = serializer.validated_data['unique_id']
            password = serializer.validated_data['password']
            session_id = serializer.validated_data['session_id']
        else:
            print(serializer.errors)
        try :
            auth_object = SubTestSessionPassword.objects.get(session = session_id)
            if(auth_object.authenticate_password(password)):
                print("pwd matched ")
                session_object = SubTestSession.objects.get(pk = session_id)
                AttendanceSubTest.objects.create(session = session_object, candidate = request.user, unique_id = unique_id)
                return Response(status= 200)
            else:
                return Response("pwds dont match", status = 201)
        except :
            return Response("session not found")
        
            
        
    

class CategorySessionAuthentication(APIView):
    """
    to authenticate user for a session test -> can also be used to take the attendace in future  
    """
    # permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        serializer = CategorySessionAuthenticationSerializer(data = request.data)
        print(serializer)
        if serializer.is_valid():
            unique_id = serializer.validated_data['unique_id']
            password = serializer.validated_data['password']
            session_id = serializer.validated_data['session_id']
        else:
            print(serializer.errors)
        try :
            auth_object = CategorySessionPassword.objects.get(session = session_id)
            if(auth_object.authenticate_password(password)):
                print("pwd matched ")
                session_object = CategoryTestSession.objects.get(pk = session_id)
                attend = AttendanceCategorySession.objects.get_or_create(session = session_object, candidate = request.user, unique_id = unique_id)
                if attend:
                    return Response(status= 200)
        except :
            return Response("session not found")    
        return Response("pwds dont match", status = 201)
    

class CombinedCategorySessionAuthentication(APIView):
    """
    to authenticate user for a session test -> can also be used to take the attendace in future  
    """

    def post(self, request, *args, **kwargs):
        serializer = CategorySessionAuthenticationSerializer(data = request.data)
        print(serializer)
        if serializer.is_valid():
            unique_id = serializer.validated_data['unique_id']
            password = serializer.validated_data['password']
            session_id = serializer.validated_data['session_id']
        else:
            print(serializer.errors)
        try :
            auth_object = CombinedCategorySessionPassword.objects.get(session = session_id)
            if(auth_object.authenticate_password(password)):
                print("pwd matched ")
                session_object = CombinedCategoryTestSession.objects.get(pk = session_id)
                AttendanceCCSession.objects.create(session = session_object, candidate = request.user, unique_id = unique_id)
                return Response(status= 200)
            else:
                return Response("pwds dont match", status = 201)
        except :
            return Response("session not found")
        
class QuestionsRetrieveAPIView(generics.ListAPIView):
    """
    similar to QuestionsRetrieveAPIView in 'tests': reason for not importing that was the use of tables add making that 
    dynamic adds unnecessary complexity and makes the code slower because of more is_instance() checks
    """
    serializer_class = QuestionSerializer

    # make this field dynamic in future
    test_lengths = {
            1 : 10,
            2 : 10,
            3 : 10,
            4 : 10,
            5 : 10,
        }
    weight_ranges = {
            (0, 50): {'easy': 6, 'medium': 3, 'hard': 1},
            (50, 80): {'easy': 5, 'medium': 4, 'hard': 1},
            (80, 100): {'easy': 4, 'medium': 4, 'hard': 2},
        }

    
    def get_counts(self, user_score, total_questions_count):
        for score_range, weights in self.weight_ranges.items():
            if score_range[0] <= user_score < score_range[1]:
                easy_weight, medium_weight, hard_weight = weights['easy'], weights['medium'], weights['hard']
                break
        else:
            # Default weights if the user's score doesn't fall into any defined range
            easy_weight, medium_weight, hard_weight = 5, 4, 1

        # formula for getting the number of questions per category for the test
        easy_questions_count = int((easy_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        medium_questions_count = int((medium_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        hard_questions_count = int((hard_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        print(easy_questions_count, medium_questions_count, hard_questions_count)

        return easy_questions_count, medium_questions_count, hard_questions_count
    
    def get_queryset(self, request):
        # category of the test
        category_id = self.kwargs['category']
        category_object = GroupTestCategory.objects.get(pk = category_id)
        test_length = self.test_lengths.get(category_id, 0)
        print(test_length)
        profile = Profile.objects.get(user =request.user)
        try:
            # --bug categories_id overlapping --later probably between category, combined_category and the other test
            #--fix query based on type and id e.g type = category, id = x (takes more space though)
            # make changes in the query based on user as well as institute
            avg_score_object = GroupTestAverageScore.objects.get(profile=profile, category=category_id)
            avg_score = avg_score_object.avg_score
        except GroupTestAverageScore.DoesNotExist:
            # store this else where
            avg_score = 60
        print(avg_score, test_length)

        easy_count , medium_count, hard_count = self.get_counts(avg_score, test_length)

        easy_questions = EasyQuestion.objects.filter(category=category_id).order_by('?')[:easy_count]
        medium_questions = MediumQuestion.objects.filter(category=category_id).order_by('?')[:medium_count]
        hard_questions = HardQuestion.objects.filter(category=category_id).order_by('?')[:hard_count]

        questions_dict = {
        'easy_questions': easy_questions,
        'medium_questions': medium_questions,
        'hard_questions': hard_questions,
    }
        return questions_dict
    
    def list(self, request, *args, **kwargs):
        print(request)
        queryset = self.get_queryset(request=request)
        instance = {'questions' : queryset}
        serializer = self.get_serializer(instance)
        print("being called")
        return Response(serializer.data)
    
class SubTestAnswerSubmitAPIView(APIView):
    scoring = {
        'easy': 5,
        'medium' : 7,
        'hard' : 10
    }
         
    def get_total_score(self, count):
        # max score of the test
        total_score = 0
        for key in count:
            if key == 'count_easy':
                total_score += count['count_easy'] * self.scoring['easy']
            elif key == 'count_medium':
                total_score += count['count_medium'] * self.scoring['medium']
            elif key == 'count_hard':
                total_score += count['count_hard'] * self.scoring['hard']
        return total_score

    def post(self, request, *args, **kwargs):
        # evaluates the choices selected for the answers
        # suggestion send the choices directly instead of sending them as (easy, mid, hard) and get the difficulty in the backend 
        data = request.data
        user = request.user
        print("inside suibmit answers")
        serializer = SubmitAnswersSerializer(data =data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
        else:
            print(serializer.errors)
        print(request.data)
        session_id  = validated_data['session']
        unique_id = validated_data['unique_id']    
        print(unique_id)
        # checks the time constraint for the test
        start_time  = AttendanceSubTest.objects.get(candidate = user,  session  = session_id, unique_id = unique_id).start_time.replace(tzinfo=timezone.utc)
        print(start_time)
        sub_test_session  = SubTestSession.objects.get(pk = session_id)
        duration = sub_test_session.duration
        end_time = sub_test_session.end_time.replace(tzinfo=timezone.utc)
        current_time = datetime.now().replace(tzinfo=timezone.utc)
        
        print(start_time, duration, end_time, "the time stuff is here" )

        if not (start_time <= current_time <= (start_time + timedelta(minutes= duration)) <= end_time):
            return Response({'detail': 'Test submission not allowed at this time.'}, status=status.HTTP_403_FORBIDDEN)
        
        easy = validated_data['choices']['easy']
        medium = validated_data['choices']['medium']
        hard = validated_data['choices']['hard']
        inst = User.objects.get(pk = validated_data['institute'])
        category = sub_test_session.sub_test.category
        session = SubTestSession.objects.get(pk = session_id)

        total_score = self.get_total_score(validated_data['count'])
        score = 0
        print('here')
        try:
            
            for answer in easy:
                choice_id = answer['answer_id']
                selected_choice = ChoiceForEasyQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score+= self.scoring['easy']
            
            for answer in medium:
                choice_id = answer['answer_id']
                selected_choice = ChoiceForMediumQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score+=self.scoring['medium']

            for answer in hard:
                choice_id = answer['answer_id']
                selected_choice = ChoiceForHardQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score+=self.scoring['hard']
            score_percentage = (score/total_score) * 100
            print("here")
        
        except :
            print("here?")
            return Response({'detail': 'Question or Choice does not exist'}, status=status.HTTP_404_NOT_FOUND)
        print("here ")
        SubTestsMarksLibrary.objects.create(institute = inst, candidate = user, score = score, session = session)
        print("not here ")

        test_lib = GroupTestScoresLibrary.objects.create(institute = inst, candidate = user, score = score_percentage, category = category )
        
        if score_percentage > 40:
            test_lib.update_average_score(institute = inst, candidate = user,  category=category)
        print(round(score_percentage, 2))
        return Response(round(score_percentage, 2))

class SubmitAnswersAPIView(APIView):
    # optimzie on taking input "category" -> no need ot fetch the category from the question object
    # check for answers, update the avg score, update the score
    # permission_classes = IsStudent
    # change this as a dynamic field depending on the actual test
    scoring = {
        'easy': 5,
        'medium' : 7,
        'hard' : 10
    }

    def get_category(self, easy_questions, medium_questions, hard_questions):
        if easy_questions:
            question = EasyQuestion.objects.get(pk = easy_questions[0]['question_id'])
            return question.category
        if medium_questions:
            question = MediumQuestion.objects.get(pk = medium_questions[0]['question_id'])
            return question.category
        if hard_questions:
            question = HardQuestion.objects.get(pk = hard_questions[0]['question_id'])
            return question.category
    
    def get_total_score(self, count):
        # max score of the test
        total_score = 0
        for key in count:
            if key == 'count_easy':
                total_score += count['count_easy'] * self.scoring['easy']
            elif key == 'count_medium':
                total_score += count['count_medium'] * self.scoring['medium']
            elif key == 'count_hard':
                total_score += count['count_hard'] * self.scoring['hard']
        return total_score
        
    
    def post(self, request, *args, **kwargs):
        # evaluates the choices selected for the answers
        # suggestion send the choices directly instead of sending them as (easy, mid, hard) and get the difficulty in the backend 

        data = request.data
        user = request.user
        serializer = SubmitAnswersSerializer(data =data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
        else:
            print(serializer.errors)

        session_id  = validated_data['session']
        unique_id = validated_data['unique_id']    

        # checks the time constraint for the test
        start_time  = AttendanceCategorySession.objects.get(candidate = user,  session  = session_id, unique_id = unique_id).start_time.replace(tzinfo=timezone.utc)
        test_session  = CategoryTestSession.objects.get(pk = session_id)
        duration = test_session.duration
        end_time = test_session.end_time.replace(tzinfo=timezone.utc)
        current_time = datetime.now().replace(tzinfo=timezone.utc)
        
        print(start_time, duration, end_time, "the time stuff is here" )

        if not (start_time <= current_time <= (start_time + timedelta(minutes= duration)) <= end_time):
            print("session expired")
            return Response({'detail': 'Test submission not allowed at this time.'}, status=status.HTTP_403_FORBIDDEN)


        easy = validated_data['choices']['easy']
        medium = validated_data['choices']['medium']
        hard = validated_data['choices']['hard']
        inst = User.objects.get(pk = validated_data['institute'])
        category = self.get_category(easy, medium, hard)
        total_score = self.get_total_score(validated_data['count'])
        session = CategoryTestSession.objects.get(pk = session_id)
        print(easy)

        score = 0
        try:
            
            for answer in easy:
                choice_id = answer['answer_id']
                selected_choice = ChoiceForEasyQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score+= self.scoring['easy']
            
            for answer in medium:
                choice_id = answer['answer_id']
                selected_choice = ChoiceForMediumQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score+=self.scoring['medium']

            for answer in hard:
                choice_id = answer['answer_id']
                selected_choice = ChoiceForHardQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score+=self.scoring['hard']
            score_percentage = (score/total_score) * 100
            print(score_percentage)

           
        except Exception:
            return Response({'detail': 'Question or Choice does not exist'}, status=status.HTTP_404_NOT_FOUND)
        GroupTestMarksLibrary.objects.create(institute = inst, candidate = user, score = score, session = session)
        test_lib = GroupTestScoresLibrary.objects.create(institute = inst, candidate = user, score = score_percentage, category = category )
        
        if score_percentage > 40:
            pass
            test_lib.update_average_score(institute = inst, candidate = user,  category=category)
        print("fine till here")
        print(round(score_percentage, 2))
        return Response(round(score_percentage, 2))
    
class SubmitCombinationAnswersAPIView(APIView):
    # migth wanna save marks in more detail in the future
    permission_classes = [permissions.IsAuthenticated]
    scoring = {
        'easy': 5,
        'medium' : 7,
        'hard' : 10
    }

    # max score of the test
    def get_max_total_score(self, count):
        total_score = 0
        for category, count_dict in count.items():
            for key , value in count_dict.items():
                if key == 'count_easy':
                    total_score += value * self.scoring['easy']
                elif key == 'count_medium':
                    total_score += value * self.scoring['medium']
                elif key == 'count_hard':
                    total_score += value * self.scoring['hard']
        return total_score
    
    def get_total_score(self, count):
        # max score of the test
        total_score = 0
        for key in count:
            if key == 'count_easy':
                total_score += count['count_easy'] * self.scoring['easy']
            elif key == 'count_medium':
                total_score += count['count_medium'] * self.scoring['medium']
            elif key == 'count_hard':
                total_score += count['count_hard'] * self.scoring['hard']
        return total_score

    def post(self, request, *args, **kwargs):
        # implement serializer for this view
        data = request.data
        user = request.user
        print(data)

        session_id  = data['session']
        unique_id = data['unique_id']

        start_time  = AttendanceCCSession.objects.get(candidate = user,  session  = session_id, unique_id = unique_id).start_time.replace(tzinfo=timezone.utc)
        cc_test_session  = CombinedCategoryTestSession.objects.get(pk = session_id)
        combined_category =CombinedCategoryTestSession.objects.get(pk = session_id).combined_category
        duration = cc_test_session.duration
        end_time = cc_test_session.end_time.replace(tzinfo=timezone.utc)
        current_time = datetime.now().replace(tzinfo=timezone.utc)
        
        print(start_time, duration, end_time, "the time stuff is here" )

        if not (start_time <= current_time <= (start_time + timedelta(minutes= duration)) <= end_time):
            print("time exceeded")
            return Response({'detail': 'Test submission not allowed at this time.'}, status=status.HTTP_403_FORBIDDEN)

        all_answers  = data['choices']
        questions_count_dict = data['count']
        institute = data['institute']
        institute = User.objects.get(pk = institute)


        # max score possible for the whole 
        max_total_score = self.get_max_total_score(questions_count_dict)

        # total_score scored by the user in the test
        total_score = 0
        # iterates the data by category
        for category, answer_set in all_answers.items():
            print(category, "this is category")
            # total score scored per category
            total_category_score = 0
            # iterates the data by difficulty
            for answer_difficulty in answer_set:
                if answer_difficulty == 'easy':
                    # iterates the data by question_id and choice_id
                    for question_id , choice_id in answer_set[answer_difficulty].items():
                        selected_choice = ChoiceForEasyQ.objects.get(pk = choice_id)
                        if selected_choice.is_correct:
                             total_category_score+= self.scoring['easy']
                             print('correct easy', total_category_score)


                elif answer_difficulty == 'medium':
                    for question_id , choice_id in answer_set[answer_difficulty].items():
                        selected_choice = ChoiceForMediumQ.objects.get(pk = choice_id)
                        if selected_choice.is_correct:
                             total_category_score+= self.scoring['medium']
                             print('correct medium', total_category_score)


                elif answer_difficulty == 'hard':
                    for question_id , choice_id in answer_set[answer_difficulty].items():
                        selected_choice = ChoiceForHardQ.objects.get(pk = choice_id)
                        if selected_choice.is_correct:
                             total_category_score+= self.scoring['hard']
                             print('correct hard', total_category_score)



            # max score per category for the test
            max_category_score = self.get_total_score(questions_count_dict[category])
            # total score scored by the user for the test
            total_score += total_category_score
            print(total_score)
            score_percentage = (total_category_score/max_category_score) *100
            # no of questions can be too small to make changes in the difficulty of upcoming tests
        total_score_percentage = (total_score/max_total_score) *100
        test_lib = CombinedGroupTestMarksLibrary.objects.create(candidate = user, score = round(total_score_percentage, 2), category = combined_category, institute = institute)

        print(total_score, "this is the total score")
        print(max_total_score, "this is the max total score")
        return Response(total_score_percentage)
    
class SubTestSessionQuestionsListAPIView(generics.ListAPIView):
    """
    serves questions to test sessions based on the category
    """
    # solve conflict for category and combined category
    serializer_class = QuestionSerializer

    def get_counts(self, user_score, total_questions_count):
        for score_range, weights in self.weight_ranges.items():
            if score_range[0] <= user_score < score_range[1]:
                easy_weight, medium_weight, hard_weight = weights['easy'], weights['medium'], weights['hard']
                break
        else:
            # Default weights if the user's score doesn't fall into any defined range
            easy_weight, medium_weight, hard_weight = 5, 4, 1

        # formula for getting the number of questions per category for the test
        easy_questions_count = int((easy_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        medium_questions_count = int((medium_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        hard_questions_count = int((hard_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        print(easy_questions_count, medium_questions_count, hard_questions_count)

        return easy_questions_count, medium_questions_count, hard_questions_count
    
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        institute = self.kwargs['inst']
        institute = institute
        subtest_obj = SubTestSession.objects.get(user = institute,  pk = session_id).sub_test
        subtest_id = subtest_obj.pk

        easy_questions = EasyQuestion.objects.filter(test=subtest_id)
        medium_questions = MediumQuestion.objects.filter(test=subtest_id)
        hard_questions = HardQuestion.objects.filter(test=subtest_id)

        questions_dict = {
        'easy_questions': easy_questions,
        'medium_questions': medium_questions,
        'hard_questions': hard_questions,
    }
        print(questions_dict)
        return questions_dict
    
    def list(self, request, *args, **kwargs):
        print(request)
        queryset = self.get_queryset()
        instance = {'questions' : queryset}
        serializer = self.get_serializer(instance)
        print("being called")
        return Response(serializer.data)

class CategoryTestSessionQuestionsListAPIView(generics.ListAPIView):
    """
    serves questions to test sessions based on the category
    """
    # solve conflict for category and combined category
    serializer_class = QuestionSerializer

    all_test_lengths = {
            1 : 10,
            2 : 10,
            3 : 10,
            4 : 10,
            5 : 10,
        }
    weight_ranges = {
            (0, 50): {'easy': 6, 'medium': 3, 'hard': 1},
            (50, 80): {'easy': 5, 'medium': 4, 'hard': 1},
            (80, 100): {'easy': 4, 'medium': 4, 'hard': 2},
        }

    def get_counts(self, user_score, total_questions_count):
        for score_range, weights in self.weight_ranges.items():
            if score_range[0] <= user_score < score_range[1]:
                easy_weight, medium_weight, hard_weight = weights['easy'], weights['medium'], weights['hard']
                break
        else:
            # Default weights if the user's score doesn't fall into any defined range
            easy_weight, medium_weight, hard_weight = 5, 4, 1

        # formula for getting the number of questions per category for the test
        easy_questions_count = int((easy_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        medium_questions_count = int((medium_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        hard_questions_count = int((hard_weight/(easy_weight + medium_weight + hard_weight)*total_questions_count))
        print(easy_questions_count, medium_questions_count, hard_questions_count)

        return easy_questions_count, medium_questions_count, hard_questions_count
    
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        institute = self.kwargs['inst']
        institute = institute
        category_obj = CategoryTestSession.objects.get(user = institute,  pk = session_id).category
        category_id = category_obj.pk

        user = self.request.user
        user = 1
        # institute = category_obj.user

        test_length = self.all_test_lengths.get(category_id, 0)
        try:
            # --bug categories_id overlapping --later probably between category, combined_category and the other test
            #--fix query based on type and id e.g type = category, id = x (takes more space though)
            avg_score_object = GroupTestAverageScore.objects.get(candidate=user, institute =  institute, category=category_id)
            avg_score = avg_score_object.avg_score
        except GroupTestAverageScore.DoesNotExist:
            # store this else where
            avg_score = 60
        easy_count , medium_count, hard_count = self.get_counts(avg_score, test_length)
        easy_questions = EasyQuestion.objects.filter(category=category_id).order_by('?')[:easy_count]
        medium_questions = MediumQuestion.objects.filter(category=category_id).order_by('?')[:medium_count]
        hard_questions = HardQuestion.objects.filter(category=category_id).order_by('?')[:hard_count]

        questions_dict = {
        'easy_questions': easy_questions,
        'medium_questions': medium_questions,
        'hard_questions': hard_questions,
    }
        print(questions_dict)
        return questions_dict
    
    def list(self, request, *args, **kwargs):
        print(request)
        queryset = self.get_queryset()
        instance = {'questions' : queryset}
        serializer = self.get_serializer(instance)
        print("being called")
        return Response(serializer.data)
    

class CombinationCategoryTestSessionQuestionsListAPIView(generics.ListAPIView):
    """
    fetches questions according to the combined category for the group test session
    """
    serializer_class = CombinedCategoryQuestionSerializer

    all_test_lenghts = {
        # 1 -> for demo combination
        1 : 10,
        2 : 10,
        3 : 10,
        4: 10,
    }
    weight_ranges = {
            (0, 50): {'easy': 6, 'medium': 3, 'hard': 1},
            (50, 80): {'easy': 5, 'medium': 4, 'hard': 1},
            (80, 100): {'easy': 4, 'medium': 4, 'hard': 2},
        }

    def get_counts(self, user_score, total_questions_count):

        for score_range, weights in self.weight_ranges.items():
            if score_range[0] <= user_score < score_range[1]:
                easy_weight, medium_weight, hard_weight = weights['easy'], weights['medium'], weights['hard']
                break
        else:
            # Default weights if the user's score doesn't fall into any defined range
            easy_weight, medium_weight, hard_weight = 5, 4, 1

        # Formula for getting the number of questions per category for the test
        total_weight = easy_weight + medium_weight + hard_weight
        if total_weight == 0:
            # Avoid division by zero
            return 0, 0, 0

        easy_questions_count = int((easy_weight / total_weight) * total_questions_count)
        medium_questions_count = int((medium_weight / total_weight) * total_questions_count)
        hard_questions_count = int((hard_weight / total_weight) * total_questions_count)

        # Ensure at least one question per category
        easy_questions_count = max(easy_questions_count, 1)
        medium_questions_count = max(medium_questions_count, 1)
        hard_questions_count = max(hard_questions_count, 1)

        return easy_questions_count, medium_questions_count, hard_questions_count
    def get_sub_categories(self, category_id, institute):
        print(institute, category_id, "inside sub_categories")
        sub_categories = GroupTestCombinedCategory.objects.get(user = institute, pk = category_id).associated_categories.all()
        sub_categories_list = [i.pk for i in sub_categories]
        return sub_categories_list
        
    
    def get_avg_scores(self, sub_categories_ids, user, institute):
        scores_dict = {}
        score_sum = 0

        
        for sub_category in sub_categories_ids:
            try :
                average_score = GroupTestAverageScore.objects.get(candidate = user, institute = institute, category =  sub_category).avg_score
            except : 
                average_score = 60 
            scores_dict[sub_category] = average_score
            score_sum += average_score
        
        return scores_dict, score_sum

    def get_count_per_category(self, scores_dict, score_sum, test_length):
        # gets the questions from each category based on the user score
        counts = {}
        sum = 0
        for item in scores_dict:
            proportion_item = scores_dict[item]/score_sum
            counts[item] = round(proportion_item * test_length)
        for item in counts:
            sum += counts[item]
        if sum < test_length:
            # get the score with the least value
            min_key = min(scores_dict, key= scores_dict.get)
            # min_key_pair = next(iter(scores_dict.items()))
            
        while(sum < test_length):
            counts[min_key] +=1
            sum += 1 
        return counts

    def get_queryset(self):
        # breaks the paper on the basis of three avg scores

        session_id = self.kwargs['session_id']
        user  =self.request.user
        institute = self.kwargs['inst']
        print(institute, session_id)
        combined_category_obj =  CombinedCategoryTestSession.objects.get(user = institute, pk = session_id).combined_category
        category_id =combined_category_obj.pk

        sub_categories_ids = self.get_sub_categories(category_id, institute)
        questions_dict = {}
        scores, score_sum = self.get_avg_scores(sub_categories_ids, user, institute )
        test_length = self.all_test_lenghts.get(category_id, 0)
        # gets the number of questions per category
        questions_count = self.get_count_per_category(scores_dict=scores, score_sum= score_sum, test_length= test_length)

        for category in sub_categories_ids:
            test_length = self.all_test_lenghts.get(category_id, 0)        
            user  = self.request.user
            user = 1
            try:
                average_score_object = GroupTestAverageScore.objects.get(candidate = 1, institute = 1, category =  category)
                average_score = average_score_object.avg_score
            except GroupTestAverageScore.DoesNotExist:
                average_score = 60
            
            easy_count, medium_count, hard_count = self.get_counts(average_score, questions_count[category])
            print(easy_count, medium_count, hard_count , " for ", category, "length = ", questions_count[category])
            
            easy_questions = EasyQuestion.objects.filter(category=category).order_by('?')[:easy_count]
            medium_questions = MediumQuestion.objects.filter(category=category).order_by('?')[:medium_count]
            hard_questions = HardQuestion.objects.filter(category=category).order_by('?')[:hard_count]

            questions_dict[category] = {
                'easy_questions': easy_questions,
                'medium_questions': medium_questions,
                'hard_questions': hard_questions,
            }
        print(questions_dict, "this is questions dict")
        return questions_dict
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # instance = {'question' : queryset}
        serializer = self.get_serializer(queryset)
        # print(serializer.data)
        return Response(serializer.data)

from django.shortcuts import render 
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView     
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework import permissions

import json

from django.contrib.auth.models import User

from user_profiles.models import Profile, AverageScore, TestScoresLibrary , TestMarksLibrary, CombinedTestScoresLibrary

from .models import (
    Test , EasyQuestion, MediumQuestion, Category,
    ChoiceForEasyQ, ChoiceForHardQ, ChoiceForMediumQ, HardQuestion, 
    CombinedTestCategory
)
from .serializers import (
    CategoryListCreateSerializer, SubmitAnswersSerializer,
    CategoryListCreateSerializer, QuestionSerializer,
    CombinationTestSerializer, CombinedCategoryQuestionSerializer,
    CreateQuestionsSerializer
)

from user_profiles.models import QuestionStatistics
# Create your views here.   

class CategoriesListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

       
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            return Response({'error': 'Only admins can create categories.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(user = self.request.user)

        
         
    
class CCListCreateAPIView(generics.ListCreateAPIView):
    queryset = CombinedTestCategory.objects.all()
    serializer_class = CombinationTestSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            return Response({'error': 'Only admins can create categories.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(user = self.request.user)

class CombinationTestQuestionsListSerializerAPIView(generics.ListAPIView):
    serializer_class = CombinedCategoryQuestionSerializer
    # serializer_class = QuestionSerializer
    # queryset = CombinedTestCategory.objects.all()

    all_test_lenghts = {
        # 1 -> for demo combination
        1 : 10,
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
    def get_sub_categories(self, category_id):
        sub_categories = CombinedTestCategory.objects.get(pk = category_id).associated_categories.all()
        sub_categories_list = [i.pk for i in sub_categories]
        return sub_categories_list
        
    
    def get_avg_scores(self, sub_categories_ids):
        scores_dict = {}
        score_sum = 0
        user = self.request.user
        profile = Profile.objects.get(user = user)

        # add exception over here in case the user has not attempted the test of this category before 
        for sub_category in sub_categories_ids:
            try :
                average_score = AverageScore.objects.get(profile = profile, category =  sub_category).avg_score
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
        while(sum < test_length):
            counts[min_key] +=1
            sum += 1 
        print(counts, "counts")
        return counts

    def get_queryset(self):
        # breaks the paper on the basis of three avg scores
        category_id = self.kwargs['category']
        sub_categories_ids = self.get_sub_categories(category_id)
        questions_dict = {}
        scores, score_sum = self.get_avg_scores(sub_categories_ids)
        test_length = self.all_test_lenghts.get(category_id, 0)
        # gets the number of questions per category
        questions_count = self.get_count_per_category(scores_dict=scores, score_sum= score_sum, test_length= test_length)

        for category in sub_categories_ids:
            test_length = self.all_test_lenghts.get(category_id, 0)        
            profile = Profile.objects.get(user = self.request.user)
            try:
                average_score_object = AverageScore.objects.get(profile = profile, category =  category)
                average_score = average_score_object.avg_score
            except AverageScore.DoesNotExist:
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

        
class QuestionsRetrieveAPIView(generics.ListAPIView):
    # --bug gets called twice
    # send questions dynamically based on the category
    serializer_class = QuestionSerializer

    # make this field dynamic in future
    all_test_lenghts = {
            'Coding' : 10,
            'Design' : 10,
            'General' : 10,
            'Interview' : 10,
            'CET' : 10,
            'Placements' : 10,
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
        category = self.kwargs['category']
        category_name = Category.objects.get(pk = category).name
        # make it get it with the id insted of the category name
        test_length = self.all_test_lenghts.get(category_name, 10)
        profile = Profile.objects.get(user =request.user)
        try:
            avg_score_object = AverageScore.objects.get(profile=profile, category=category)
            avg_score = avg_score_object.avg_score
        except AverageScore.DoesNotExist:
            # store this else where
            avg_score = 60

        easy_count , medium_count, hard_count = self.get_counts(avg_score, test_length)

        easy_questions = EasyQuestion.objects.filter(category=category).order_by('?')[:easy_count]
        medium_questions = MediumQuestion.objects.filter(category=category).order_by('?')[:medium_count]
        hard_questions = HardQuestion.objects.filter(category=category).order_by('?')[:hard_count]

        questions_dict = {
        'easy_questions': easy_questions,
        'medium_questions': medium_questions,
        'hard_questions': hard_questions,
    }
        return questions_dict
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request=request)
        instance = {'questions' : queryset}
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class SubmitCombinationAnswersAPIView(APIView):
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
        data = request.data
        user = request.user
        profile = Profile.objects.get(user = user)

        # answers dict
        all_answers = data['answers']
        # total number of questions in the dict
        questions_count_dict = data['count']
        combined_category = data['category']
        combined_category_instance = CombinedTestCategory.objects.get(pk = combined_category)
        # max score possible for the whole test
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
            score_percentage = (total_category_score/max_category_score) *100
            # the below line might work for the tests for the students -> cause numeber of questions is too small to make changes in the difficulty of questions according to them
            # test_lib = TestScoresLibrary.objects.create(profile = profile, score = round(score_percentage, 2), category = category)
            # if score_percentage > 40:
            #     test_lib.update_average_score(profile= profile, category=category)
        total_score_percentage = (total_score/max_total_score) *100
        test_lib = CombinedTestScoresLibrary.objects.create(profile = profile, score = round(total_score_percentage, 2), category = combined_category_instance)

        print(total_score, "this is the total score")
        print(max_total_score, "this is the max total score")
        return Response(total_score_percentage)


class SubmitAnswersAPIView(APIView):
    # dependencies (category, questions, number of questions)
    # check for answers, update the avg score, update the score

    permission_classes = [permissions.IsAuthenticated]
    
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
        serializer = SubmitAnswersSerializer(data =data)
        print(request.data)
        if serializer.is_valid():
            print("valid")
            validated_data = serializer.validated_data
        else:
            print(serializer.errors)

        easy = validated_data['choices']['easy']
        medium = validated_data['choices']['medium']
        hard = validated_data['choices']['hard']

        profile = Profile.objects.get(name= request.user)
        category = self.get_category(easy, medium, hard)
        statistics , created= QuestionStatistics.objects.get_or_create(user = request.user, category = category)

        total_score = self.get_total_score(validated_data['count'])
        score =0
        try:
            
            for answer in easy:
                choice_id = answer['answer_id']
                question_id = answer['question_id']
                selected_choice = ChoiceForEasyQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    statistics.easy_count.add(question_id)
                    score+= self.scoring['easy']
            
            for answer in medium:
                choice_id = answer['answer_id']
                question_id = answer['question_id']
                selected_choice = ChoiceForMediumQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    statistics.medium_count.add(question_id)
                    score+=self.scoring['medium']

            for answer in hard:
                choice_id = answer['answer_id']
                question_id = answer['question_id']
                selected_choice = ChoiceForHardQ.objects.get(pk = choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    statistics.hard_count.add(question_id)
                    score+=self.scoring['hard']
            score_percentage = (score/total_score) *100
            print("The marks are :", score)
            TestMarksLibrary.objects.create(profile = profile, score = score, category = category)
            test_lib = TestScoresLibrary.objects.create(profile = profile, score = score_percentage, category = category )
            print(test_lib)
            if score_percentage > 40:
                test_lib.update_average_score(profile= profile, category=category)
                print("coming here")

        except Exception as e:
            print(e)
            return Response({'detail': 'Question or Choice does not exist'}, status=status.HTTP_404_NOT_FOUND)
        print("the score is" ,round(score_percentage, 2))
        return Response(round(score_percentage, 2))
    
class QuestionsCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateQuestionsSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CreateQuestionsSerializer(data = data, context = {'request' : request})
        print(data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

import pandas as pd

from rest_framework import serializers

from django.contrib.auth.models import User

from .models import (
    Test, Category, EasyQuestion, MediumQuestion, 
    HardQuestion, ChoiceForEasyQ ,ChoiceForMediumQ, 
    ChoiceForHardQ, CombinedTestCategory, Test
    )

from user_profiles.models import AverageScore
from pandas.errors import ParserError
from django.core.exceptions import ObjectDoesNotExist      


class EasyChoiceSerializer(serializers.ModelSerializer):
    difficulty = serializers.SerializerMethodField()
    class Meta:
        model = ChoiceForEasyQ
        fields = ['pk', 'text', 'is_correct', 'difficulty']
    
    def get_difficulty(self, obj):
        return "easy"

class MediumChoiceSerializer(serializers.ModelSerializer):
    difficulty = serializers.SerializerMethodField()
    class Meta:
        model = ChoiceForMediumQ
        fields = ['pk', 'text', 'is_correct', 'difficulty']
    
    def get_difficulty(self, obj):
        return "medium"

class HardChoiceSerializer(serializers.ModelSerializer):
    difficulty = serializers.SerializerMethodField()
    class Meta:
        model = ChoiceForHardQ
        fields = ['pk', 'text', 'is_correct', 'difficulty']

    def get_difficulty(self, obj):
        return "hard"


class EasyQuestionListSerializer(serializers.ModelSerializer):
    choices = EasyChoiceSerializer(source = 'choiceforeasyq_set', read_only = True, many =True)
    class Meta:
        model = EasyQuestion
        fields = [
            'pk',
            'text',
            'choices',
            'category',
        ]

    

class MediumQuestionListSerializer(serializers.ModelSerializer):
    choices = EasyChoiceSerializer(source = 'choiceformediumq_set', read_only = True, many =True)
    class Meta:
        model = MediumQuestion
        fields = [
            'pk',
            'text',
            'choices',
            'category',


        ]


class HardQuestionListSerializer(serializers.ModelSerializer):
    choices = EasyChoiceSerializer(source = 'choiceforhardq_set', read_only = True, many =True)
    class Meta:
        model = HardQuestion
        fields = [
            'pk',
            'text',
            'choices',
            'category',

        ]

class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'pk',
            'name',
            'description',
        ]
        # exclude = ['difficulty']

class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields =  [
            'title',
            'difficulty',
            'description',
            'category',
            'test_file',

        ]

class CombinationTestSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = CombinedTestCategory
        fields = [
            'pk',
            'username',
            'name',
            'associated_categories',
            'description',
        ]

    def get_username(self, obj):
        return obj.get_username()



class QuestionListSerializer(serializers.ModelSerializer):
    # xp = serializers.SerializerMethodField(read_only = True)
    easy_questions = EasyQuestionListSerializer(source = 'easyquestion_set', many=True, read_only=True)
    medium_questions = MediumQuestionListSerializer(source='mediumquestion_set', many=True, read_only=True)    
    hard_questions = HardQuestionListSerializer(source='hardquestion_set', many=True, read_only=True)

    class Meta:
        model = Test
        fields = [
            'pk',
            'title',
            'category',
            'easy_questions',
            'medium_questions',
            'hard_questions'
        ]
        depth = 0

    def to_representation(self, instance):
        # Limit the number of easy questions to 5 (change the limit as needed)
        # xp
        # total_questions = x
        # use total questions and xp to set the individual limit for the questions
        limit = 2
        queryset1 = instance.easyquestion_set.all()[:limit]
        queryset2 = instance.mediumquestion_set.all()[:limit]
        queryset3 = instance.hardquestion_set.all()[:limit]
        


        # Serialize the limited queryset
        easy_questions_data = EasyQuestionListSerializer(queryset1, many=True).data
        medium_questions_data = EasyQuestionListSerializer(queryset2, many=True).data
        hard_questions_data = EasyQuestionListSerializer(queryset3, many=True).data
        # Add the serialized data to the representation
        # representation = super(TestListSerializer, self).to_representation(instance)
        representation = super().to_representation(instance)
        # category_name = Category.objects.get(id= instance.category)
        # representation['category'] = CategoryListCreateSerializer(instance.category).data
        representation['easy_questions'] = easy_questions_data
        representation['medium_questions'] = medium_questions_data
        representation['hard_questions'] = hard_questions_data
        # representation['total_questions'] = total_questions
        return representation
    

class CombinedCategoryQuestionSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        category_data = {}
        for category_id, question_data in instance.items():
            easy_serializer = EasyQuestionListSerializer(question_data['easy_questions'], many = True, read_only = True)
            medium_serializer = MediumQuestionListSerializer(question_data['medium_questions'], many = True, read_only = True)
            hard_serializer = HardQuestionListSerializer(question_data['hard_questions'], many = True, read_only = True)

            category_data[category_id] = {
                'easy_questions' : easy_serializer.data,
                'medium_questions': medium_serializer.data,
                'hard_questions': hard_serializer.data,
            }
        
        print(category_data)
        return category_data

class QuestionSerializer(serializers.BaseSerializer):

    # send the questions based on category
    def to_representation(self, instance):
        # instance is the queryset sent by the view 

        easy_serializer = EasyQuestionListSerializer(instance['questions']['easy_questions'], many = True, read_only = True)
        medium_serializer = MediumQuestionListSerializer(instance['questions']['medium_questions'], many = True, read_only = True)
        hard_serializer = HardQuestionListSerializer(instance['questions']['hard_questions'], many = True, read_only = True)

        representation = {
            'easy_questions': easy_serializer.data,
            'medium_questions': medium_serializer.data,
            'hard_questions': hard_serializer.data,
        }
        return representation
    

# for accepting answers from the front end
class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()

class DifficultyAnswerSerializer(serializers.Serializer):
    difficulty = serializers.CharField()
    answers = AnswerSerializer(many=True)

class ChoicesSerializer(serializers.Serializer):
    # for the choices as answers of the test from the front-end
    easy = serializers.ListField(child=serializers.DictField())
    medium = serializers.ListField(child=serializers.DictField())
    hard = serializers.ListField(child=serializers.DictField())

class QuestionsCountSerializer(serializers.Serializer):
    # total number of questions in the test for evaluations of marks percentage w.r.t total 
    count_easy = serializers.IntegerField()
    count_medium = serializers.IntegerField()
    count_hard = serializers.IntegerField()

class SubmitAnswersSerializer(serializers.Serializer):
    # recieves marked choices and total questions from the front-end

    # session and institute is used for group tests 
    session   = serializers.IntegerField(required = False)
    institute  = serializers.IntegerField(required = False)
    unique_id  = serializers.CharField(max_length = 50, required = False)
    
    count = QuestionsCountSerializer()
    choices = ChoicesSerializer()

class CreateQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'pk',
            'name',
            'description',
            'category',
]
        
    def validate(self, data):
        # Manually validate the files
        easy_test_file = self.context['request'].FILES.get('easy_test_file')
        medium_test_file = self.context['request'].FILES.get('medium_test_file')
        hard_test_file = self.context['request'].FILES.get('hard_test_file')

        if not (easy_test_file or medium_test_file or hard_test_file):
            raise serializers.ValidationError("Need at least one of the files required.")
        
        return data
        
    def create(self, validated_data):
        instance = super().create(validated_data)
        self.post_create(instance)
        return instance
    
    def post_create(self, instance):
        test_instance = instance
        easy_test_file = self.context['request'].FILES.get('easy_test_file', None)
        medium_test_file = self.context['request'].FILES.get('medium_test_file', None)
        hard_test_file = self.context['request'].FILES.get('hard_test_file', None)

        if easy_test_file:
            self.import_quiz_from_excel(test_instance, easy_test_file, 'easy')
        if medium_test_file:
            self.import_quiz_from_excel(test_instance,medium_test_file, 'medium')

        if hard_test_file:
            self.import_quiz_from_excel(test_instance, hard_test_file, 'hard')

    
    def import_quiz_from_excel(self, group_test_instance, test_file, difficulty):
        # read the excel file
        try:
            df = pd.read_excel(test_file)
            # iterate over the each row
            for index, row in df.iterrows():
                # extract question text, choices and correct answer from the row
                question_text = str(row['Question'])
                choice1, choice2, choice3, choice4 = str(row['A']), str(row['B']), str(row['C']), str(row['D'])
                correct_answer = str(row['Answer'])

                if(difficulty == 'easy'):
                    question = EasyQuestion.objects.get_or_create(test=group_test_instance, text=question_text)
                    choice_1 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
                    choice_2 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
                    choice_3 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
                    choice_4 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')
                    
                elif(difficulty == 'medium'):
                    question = MediumQuestion.objects.get_or_create(test=group_test_instance, text=question_text)
                    choice_1 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
                    choice_2 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
                    choice_3 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
                    choice_4 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')

                elif(difficulty =='hard'):
                    question = HardQuestion.objects.get_or_create(test=group_test_instance, text=question_text)
                    choice_1 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
                    choice_2 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
                    choice_3 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
                    choice_4 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')
        except FileNotFoundError:
            print("File not found.")
        except ParserError:
            print("Error parsing the Excel file.")
        except KeyError as e:
            print(f"KeyError: {e} column not found.")
        except ObjectDoesNotExist:
            print("Related object does not exist.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")





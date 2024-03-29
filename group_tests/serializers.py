from rest_framework import serializers
import pandas as pd

from .models import (GroupTest, GroupTestCategory, GroupTestCombinedCategory,
                     SubTestSessionPassword, GroupTestPassword, CategoryTestSession, CategorySessionPassword, 
                    CombinedCategoryTestSession, CombinedCategorySessionPassword, SubTestSession,
                    EasyQuestion, MediumQuestion, 
                    HardQuestion, ChoiceForEasyQ ,ChoiceForMediumQ, 
                    ChoiceForHardQ, 
)
from pandas.errors import ParserError
from django.core.exceptions import ObjectDoesNotExist      
class GroupTestSerializer(serializers.ModelSerializer):
# for creating of group test
    class Meta:
        model = GroupTest
        fields = [
            'pk',
            'name',
            'description',
            'category',

]
    def validate(self, data):
        # Manually validate the files
        easy_test_file = self.context['request'].FILES.get('easy_test_file', None)
        medium_test_file = self.context['request'].FILES.get('medium_test_file', None)
        hard_test_file = self.context['request'].FILES.get('hard_test_file', None)

        if not (easy_test_file or medium_test_file or hard_test_file):
            raise serializers.ValidationError("Need at least one of the files required.")
        return data
        
    def create(self, validated_data):
        instance = super().create(validated_data)
        print(instance, "instance")
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

    def import_quiz_from_excel(self,group_test_instance,  test_file, difficulty):
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupTestCategory
        fields = [
            'pk',
            'name'
        ]


class CombinedCategorySerializer(serializers.ModelSerializer):
    associated_categories  = CategorySerializer(many = True, read_only=True)
    
    class Meta:
        model = GroupTestCombinedCategory
        fields = [
            'pk',
            'name',
            'associated_categories',
        ]


class SubTestPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTestSessionPassword
        fields = [
            'session',
            'password'
        ]

        extra_kwargs = {
            'password' : {'write_only'  :True}
        }

class SubTestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTestSession
        fields = [
            'pk',
            'name',
            'has_password',
            'start_time',
            'end_time',
            'sub_test',
            'duration',
        ]


class CategoryTestSessionSerializer(serializers.ModelSerializer):
    """
    for creating test sessions based on the category
    """
    class Meta:
        model = CategoryTestSession
        fields = [
            'pk',
            'name',
            'has_password',
            'start_time',
            'end_time',
            'category',
            'duration',
        ]

class CombinedCategoryTestSessionSerializer(serializers.ModelSerializer):
    """
    for creating test sessions based on the category
    """
    class Meta:
        model = CombinedCategoryTestSession
        fields = [
            'pk',
            'name',
            'has_password',
            'start_time',
            'end_time',
            'combined_category',
            'duration',
        ]
        

class CategoryPasswordSerializer(serializers.ModelSerializer):
    """
    saves passowrds for CategegoryTestSessionSerializer
    """
    class Meta:
        model = CategorySessionPassword
        fields = [
            'session',
            'password'
        ]

        extra_kwargs = {
            'password' : {'write_only'  :True}
        }



class CombinedCategoryPasswordSerializer(serializers.ModelSerializer):
    """
    saves passowrds for CategegoryTestSessionSerializer
    """
    class Meta:
        model = CombinedCategorySessionPassword
        fields = [
            'session',
            'password'
        ]

        extra_kwargs = {
            'password' : {'write_only'  :True}
        }

class CategorySessionAuthenticationSerializer(serializers.Serializer):
    session_id  = serializers.IntegerField()
    unique_id = serializers.CharField(max_length = 20)
    password = serializers.CharField(max_length = 50)


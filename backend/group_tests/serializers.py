from rest_framework import serializers
import pandas as pd

from .models import (GroupTest, GroupTestCategory, GroupTestCombinedCategory,
                     SubTestSessionPassword, GroupTestPassword, CategoryTestSession, CategorySessionPassword, 
                    CombinedCategoryTestSession, CombinedCategorySessionPassword, SubTestSession,
                    EasyQuestion, MediumQuestion, 
                    HardQuestion, ChoiceForEasyQ ,ChoiceForMediumQ, 
                    ChoiceForHardQ, 
)
                     
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
        easy_test_file = self.context['request'].FILES.get('easy_test_file')
        medium_test_file = self.context['request'].FILES.get('medium_test_file')
        hard_test_file = self.context['request'].FILES.get('hard_test_file')

        if not (easy_test_file or medium_test_file or hard_test_file):
            raise serializers.ValidationError("Need at least one of the files required.")
        
        return data
        
    def create(self, validated_data):
        easy_test_file = validated_data.pop('easy_test_file', None)
        medium_test_file = validated_data.pop('medium_test_file', None)
        hard_test_file = validated_data.pop('hard_test_file', None)

        if easy_test_file:
            self.import_quiz_from_excel(easy_test_file, 'easy')
        if medium_test_file:
            self.import_quiz_from_excel(medium_test_file, 'medium')
        if hard_test_file:
            self.import_quiz_from_excel(hard_test_file, 'hard')
        return super().create(validated_data)
    
    def import_quiz_from_excel(self, test_file, difficulty):
        # read the excel file
        df = pd.read_excel(test_file.path)

        # iterate over the each row
        for index, row in df.iterrows():
            # extract question text, choices and correct answer from the row
            question_text = row['Question']
            choice1, choice2, choice3, choice4 = row['A'], row['B'], row['C'], row['D']
            correct_answer = row['Answer']

            if(difficulty == 'easy'):
                question = EasyQuestion.objects.get_or_create(test=self, text=question_text)
                choice_1 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
                choice_2 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
                choice_3 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
                choice_4 = ChoiceForEasyQ.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')
                
            elif(difficulty == 'medium'):
                question = MediumQuestion.objects.get_or_create(test=self, text=question_text)
                choice_1 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
                choice_2 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
                choice_3 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
                choice_4 = ChoiceForMediumQ.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')

            elif(difficulty =='hard'):
                question = HardQuestion.objects.get_or_create(test=self, text=question_text)
                choice_1 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
                choice_2 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
                choice_3 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
                choice_4 = ChoiceForHardQ.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')




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


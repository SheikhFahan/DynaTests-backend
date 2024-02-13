from collections.abc import Iterable
from django.db import models
import pandas as pd

# for dynamic foreign keys
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(User, default = 1, on_delete = models.PROTECT )
    name = models.CharField(max_length=15)
    description = models.CharField(max_length = 100, default = "Defalult Description a quick brown fox jumps over a lazy dog.")

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Test(models.Model):
    """
    allows user to upload test of a paticular category -> questions can be fetched out of all categories
    or even as individual tests
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    user = models.ForeignKey(User, on_delete = models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    easy_test_file = models.FileField(upload_to='media/test_files/')
    medium_test_file = models.FileField(upload_to='media/test_files/')
    hard_test_file = models.FileField(upload_to='media/test_files/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # make changes in the test test retrieval incase any of the categories have no questions
        super().save(*args, **kwargs)
        if self.easy_test_file:
            self.import_quiz_from_excel(self.easy_test_file, 'easy')
        if self.medium_test_file:
            self.import_quiz_from_excel(self.medium_test_file, 'medium')
        if self.hard_test_file:
            self.import_quiz_from_excel(self.hard_test_file, 'hard')

    #extract excel file
    def import_quiz_from_excel(self, test_file, difficulty):
        # read the excel file
        df = pd.read_excel(test_file.path)

        # iterate over the each row
        for index, row in df.iterrows():
            # extract question text, choices and correct answer from the row
            question_text = row['Question']
            choice1, choice2, choice3, choice4 = row['A'], row['B'], row['C'], row['D']
            correct_answer = row['Answer']

            
            # for dynamic foreign key(not usefull for now)
                # getting the foreign key reference 
                # content_type = ContentType.objects.get_for_model(self)
                # create the question object
                # question = Question.objects.get_or_create(content_type = content_type, object_id = self.id, text=question_text)

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




class EasyQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null = True, blank = True, default= 'Coding')

    def save(self, *args, **kwargs):
        self.category = self.test.category
        super().save(*args, **kwargs)



    # generic-foreign-key
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # test = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.text[:50]
    
class MediumQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null = True, blank = True, default= 'Coding')

    def save(self, *args, **kwargs):
        self.category = self.test.category
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text[:50]
    
class HardQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null = True, blank = True, default= 'Coding')

    def save(self, *args, **kwargs):
        self.category = self.test.category
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text[:50]
    
class ChoiceForEasyQ(models.Model):
    question = models.ForeignKey(EasyQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:50]}, {self.text[:20]}"
    
class ChoiceForMediumQ(models.Model):
    question = models.ForeignKey(MediumQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:50]}, {self.text[:20]}"
    
class ChoiceForHardQ(models.Model):
    question = models.ForeignKey(HardQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:50]}, {self.text[:20]}"
    

class CombinedTestCategory(models.Model):
    user = models.ForeignKey(User,default = 1, on_delete = models.PROTECT)
    name = models.CharField(max_length= 20)
    associated_categories = models.ManyToManyField(Category)
    description = models.CharField(max_length = 100, default = "Defalult Description a quick brown fox jumps over a lazy dog.")


    def get_username(self):
        return  str(self.user.username)

    def __str__(self) -> str:
        return self.name
    

from django.db import models

# Create your models here.
from collections.abc import Iterable
from django.db import models
from django.utils import timezone
import pandas as pd

# for dynamic foreign keys

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password


class GroupTestCategory(models.Model):
    """
    category created by the institution should be limited to the institution
    """
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(max_length=15)

    class Meta:
        verbose_name_plural = 'Group Test Categories'

    def __str__(self):
        return self.name
    
class GroupTestCombinedCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    name = models.CharField(max_length= 20)
    associated_categories = models.ManyToManyField(GroupTestCategory)

    def get_username(self):
        return  str(self.user.username)

    def __str__(self) -> str:
        return self.name
    
class BaseTestSession(models.Model): 
    """
    to create test session based on categories and combined categories
    """
    # check the need to add blank and null = true
    # user -> institute
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    has_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(default = 20)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class CategoryTestSession(BaseTestSession):
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE)

class CombinedCategoryTestSession(BaseTestSession):
    combined_category = models.ForeignKey(GroupTestCombinedCategory, on_delete=models.CASCADE)



class CategorySessionPassword(models.Model):
    """
        saves passwords for the test for category based sessions
        -> can also add a user field over here not needed though for now
    """
    session = models.ForeignKey(CategoryTestSession, on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return f'{self.session.pk} test by {self.session.user}'

    def authenticate_password(self,  raw_password):
        if check_password(raw_password, self.password):
            return True
        return False


class CombinedCategorySessionPassword(models.Model):
    """
        saves passwords for the test for a group of people
    """
    session = models.ForeignKey(CombinedCategoryTestSession, on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return f'{self.session.pk} test by {self.session.user}'
    
    def authenticate_password(self,  raw_password):
        return check_password(raw_password, self.password)


class GroupTest(models.Model):
    # create check if the choices are more than four
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    # change the blank field later
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # difficulty = models.CharField(max_length=10,choices= DIFFICULTY_CHOICES)
    description = models.TextField()
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    def __str__(self):
        return self.name
    
    
class SubTestSession(BaseTestSession):
    sub_test  = models.ForeignKey(GroupTest, on_delete = models.CASCADE)

class SubTestSessionPassword(models.Model):
    """
        saves passwords for the test for a group of people
    """
    session = models.OneToOneField(SubTestSession, on_delete=models.CASCADE, related_name='password_info')
    password = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return f'{self.session.pk} test by {self.session.user}'
    
    def authenticate_password(self,  raw_password):
        if check_password(raw_password, self.password):
            return True
        print(self.password, raw_password)
        
        return False


class EasyQuestion(models.Model):
    test = models.ForeignKey(GroupTest, on_delete=models.CASCADE, related_name = 'easy_question')
    text = models.TextField()
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE, null = True, blank = True, related_name = 'easy_question')

    def save(self, *args, **kwargs):
        self.category = self.test.category
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text[:50]
    
class MediumQuestion(models.Model):
    test = models.ForeignKey(GroupTest, on_delete=models.CASCADE, related_name = 'medium_question')
    text = models.TextField()    
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE, null = True, blank = True, related_name = 'medium_question')

    def save(self, *args, **kwargs):
        self.category = self.test.category
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text[:50]
    
class HardQuestion(models.Model):
    test = models.ForeignKey(GroupTest, on_delete=models.CASCADE, related_name = 'hard_question')
    text = models.TextField()
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE, null = True, blank = True, related_name = 'hard_question')

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
    
    
class GroupTestPassword(models.Model):
    # stores password for the combined categorical tests for a group of people
    test = models.OneToOneField(GroupTestCombinedCategory, on_delete=models.CASCADE, related_name='password_info')
    password = models.CharField(max_length=100)

class SubTestsMarksLibrary(models.Model):
    institute = models.ForeignKey(User, related_name = "institute_subtest_test_marks",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_subtest_test_marks", on_delete=models.CASCADE)
    score = models.IntegerField()
    session = models.ForeignKey(SubTestSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def update_average_score(cls, user, session):
        avg_score = cls.objects.filter(session = session, user = user).aggregate(models.Avg('score'))['score__avg']
        SubTestSessionScoreSummary.objects.update_or_create(user= user, session = session, defaults={'score' : avg_score} )

    class Meta:
        unique_together = ['session', 'candidate', 'institute']

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.session}, {self.score}"
  
  
class GroupTestMarksLibrary(models.Model):
    """
    saves tests info on sessions
    """
    institute = models.ForeignKey(User, related_name = "institute_group_test_marks_lib",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_group_test_marks_lib", on_delete=models.CASCADE)
    score = models.IntegerField()
    session = models.ForeignKey(CategoryTestSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def update_average_score(cls, user, session):
        avg_score = cls.objects.filter(session = session, user = user).aggregate(models.Avg('score'))['score__avg']
        CategoryTestSessionScoreSummary.objects.update_or_create(user= user, session = session, defaults={'score' : avg_score} )

    class Meta:
        unique_together = ['session', 'candidate', 'institute']

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.session}, {self.score}"


class CombinedGroupTestMarksLibrary(models.Model):
    institute = models.ForeignKey(User, related_name = "institute_group_test_combined_scores",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_group_test_scores", on_delete=models.CASCADE)
    score = models.IntegerField()
    session = models.ForeignKey(CombinedCategoryTestSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def update_average_score(cls, user, session):
        avg_score = cls.objects.filter(session = session, user = user).aggregate(models.Avg('score'))['score__avg']
        CCSessionScoreSummary.objects.update_or_create(user= user, session = session, defaults={'score' : avg_score} )

    class Meta:
        unique_together = ['session', 'candidate', 'institute']

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.session}, {self.score}"
      
class SubTestSessionScoreSummary(models.Model):
    institute = models.ForeignKey(User, on_delete = models.CASCADE)
    session = models.ForeignKey(SubTestsMarksLibrary, on_delete = models.CASCADE)
    # avg score of the whose session 
    score = models.IntegerField()

    def __str__(self):
        return f"{self.institute} {self.session} {self.score}"
    
class CategoryTestSessionScoreSummary(models.Model):
    institute = models.ForeignKey(User, on_delete = models.CASCADE)
    session = models.ForeignKey(GroupTestMarksLibrary, on_delete = models.CASCADE)
    # avg score of the whose session 
    score = models.IntegerField()

    def __str__(self):
        return f"{self.institute} {self.session} {self.score}"
    
class CCSessionScoreSummary(models.Model):
    institute = models.ForeignKey(User, on_delete = models.CASCADE)
    session = models.ForeignKey(CombinedGroupTestMarksLibrary, on_delete = models.CASCADE)
    # avg score of the whose session 
    score = models.IntegerField()

    def __str__(self):
        return f"{self.institute} {self.session} {self.score}"
from django.db import models
from django.contrib.auth.models import User
from tests.models import Category, CombinedTestCategory

from group_tests.models import GroupTestCategory
from tests.models import EasyQuestion, MediumQuestion, HardQuestion

# change profile to user as the foreign key relation


class Profile(models.Model):
    """
    saves profile information about the user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_user')
    name = models.CharField(max_length= 100, null= True)
    email = models.EmailField(max_length= 30)
    address = models.CharField(max_length = 100, default = "Please Enter you address")
    phone = models.CharField(max_length=13, blank= False)
    
    def __str__(self):
        if self.name :
            return self.name
        return 'learn to code first'


class TestScoresLibrary(models.Model):
    """
    used to save score_percentage to generate the test accoring to the difficulty
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # change score to score_percentage 
    score = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def update_average_score(cls, profile, category):
        avg_score = cls.objects.filter(category = category, profile = profile).aggregate(models.Avg('score'))['score__avg']
        AverageScore.objects.update_or_create(profile= profile, category = category, defaults={'avg_score' : avg_score} )

    def __str__(self) :
        return f"{self.profile.name}, {self.category}, {self.score}"
    
    
class AverageScore(models.Model):
    """
    dependent on TestScoresLibrary for objects
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    avg_score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['category', 'profile']

    def __str__(self) :
        return f"{self.profile.name}, {self.category}, {self.avg_score}"
    
class TestMarksLibrary(models.Model):
    """
    used to save marks to show show growth on the 
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    score = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return f"{self.profile.name}, {self.category}, {self.score}"    


class CombinedTestScoresLibrary(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    score = models.IntegerField()
    category = models.ForeignKey(CombinedTestCategory, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return f"{self.profile.name}, {self.category}, {self.score}"
    
class QuestionStatistics(models.Model):
    user   = models.ForeignKey(User, on_delete = models.CASCADE)
    # change the default later to zero
    category  = models.ForeignKey(Category, on_delete = models.CASCADE,default = 1)
    easy_count = models.ManyToManyField(EasyQuestion)
    medium_count = models.ManyToManyField(MediumQuestion)
    hard_count = models.ManyToManyField(HardQuestion)
    

    def __str__(self) -> str:
        return f'{self.user}'

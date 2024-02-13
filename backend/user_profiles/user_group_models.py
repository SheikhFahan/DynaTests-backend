from django.db import models
from django.contrib.auth.models import User

from group_tests.models import (GroupTestCategory, GroupTestCombinedCategory, SubTestSession,
                                CategoryTestSession, CombinedCategoryTestSession)

# change profile to user as the foreign key relation

    
class InstituteProfile(models.Model):
    """
    saves profile information for colleges
    """
    # try finding api for university and college names
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    college_name = models.CharField(max_length= 100, null= True)
    email = models.EmailField(max_length= 30)
    phone = models.IntegerField()
    university_name = models.CharField(max_length= 100, null= True)
    address = models.CharField(max_length=255, blank=True, null=True)

class AttendanceSubTest(models.Model):
    candidate = models.ForeignKey(User ,related_name = "candidate_sub_test_attendance", on_delete=models.CASCADE)
    unique_id = models.CharField(max_length = 20)
    session = models.ForeignKey(SubTestSession,  on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['candidate', 'session', 'unique_id']

    def __str__(self) -> str:
        return f'{self.unique_id} for {self.session} '

class AttendanceCategorySession(models.Model):
    candidate = models.ForeignKey(User ,related_name = "candidate_category_session_attendance", on_delete=models.CASCADE)
    unique_id = models.CharField(max_length = 20)
    session = models.ForeignKey(CategoryTestSession,  on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['candidate', 'session', 'unique_id']

    def __str__(self) -> str:
        return f'{self.unique_id} for {self.session} '


class AttendanceCCSession(models.Model):
    candidate = models.ForeignKey(User ,related_name = "candidate_cc_session_attendance", on_delete=models.CASCADE)
    unique_id = models.CharField(max_length = 20)
    session = models.ForeignKey(CombinedCategoryTestSession,  on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['candidate', 'session', 'unique_id']

    def __str__(self) -> str:
        return f'{self.unique_id} for {self.session} '
    
class GroupTestScoresLibrary(models.Model):
    """
    saves the percentage score  to create dynamic question_sets and generate the avg test score 
    """
    institute = models.ForeignKey(User, related_name = "institute_group_test_library",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_group_test_library", on_delete=models.CASCADE)
    score = models.IntegerField()
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def update_average_score(cls, institute, candidate, GroupTestCategory):
        avg_score = cls.objects.filter(category = GroupTestCategory, candidate = candidate, institute = institute).aggregate(models.Avg('score'))['score__avg']
        GroupTestAverageScore.objects.update_or_create(candidate = candidate, institute = institute, category = GroupTestCategory, defaults={'avg_score' : avg_score} )

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.category}, {self.score}"
    
    
class GroupTestAverageScore(models.Model):
    """
    saves the average scores of the user per categroy
    """
    institute = models.ForeignKey(User, related_name = "institute_group_test_avg_score",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_group_test_avg_score", on_delete=models.CASCADE)
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE)
    avg_score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['category', 'candidate', 'institute']

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.category}, {self.avg_score}"
    
class GroupTestMarksLibrary(models.Model):
    institute = models.ForeignKey(User, related_name = "institute_group_test_marks_lib",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_group_test_marks_lib", on_delete=models.CASCADE)
    score = models.IntegerField()
    category = models.ForeignKey(GroupTestCategory, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.category}, {self.score}"


class CombinedGroupTestScoresLibrary(models.Model):
    institute = models.ForeignKey(User, related_name = "institute_group_test_combined_scores",  on_delete=models.CASCADE)
    candidate = models.ForeignKey(User ,related_name = "candidate_group_test_scores", on_delete=models.CASCADE)
    score = models.IntegerField()
    category = models.ForeignKey(GroupTestCombinedCategory, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return f"{self.institute}, {self.candidate}, {self.category}, {self.score}"


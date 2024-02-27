from django.contrib import admin

from .models import Profile, TestScoresLibrary, AverageScore, TestMarksLibrary, CombinedTestScoresLibrary, QuestionStatistics
from .user_group_models import  (
    GroupTestScoresLibrary, GroupTestAverageScore, 
    InstituteProfile, AttendanceSubTest, AttendanceCategorySession, AttendanceCCSession,
    
)


admin.site.register(Profile)
admin.site.register(TestScoresLibrary)
admin.site.register(AverageScore)
admin.site.register(TestMarksLibrary)
admin.site.register(CombinedTestScoresLibrary)
admin.site.register(GroupTestScoresLibrary)
admin.site.register(GroupTestAverageScore)
admin.site.register(InstituteProfile)
admin.site.register(AttendanceSubTest)
admin.site.register(AttendanceCategorySession)
admin.site.register(AttendanceCCSession)
admin.site.register(QuestionStatistics)

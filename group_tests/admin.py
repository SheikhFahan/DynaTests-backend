from django.contrib import admin

# Register your models here.
from .models import (
    GroupTest, GroupTestCategory, EasyQuestion, 
    MediumQuestion, HardQuestion, ChoiceForEasyQ,
    ChoiceForMediumQ, ChoiceForHardQ, GroupTestCombinedCategory,
    SubTestSessionPassword, CategoryTestSession, CategorySessionPassword, 
    CombinedCategoryTestSession,CombinedCategorySessionPassword, SubTestSession,
    GroupTestMarksLibrary, CombinedGroupTestMarksLibrary,  SubTestsMarksLibrary,
    SubTestSessionScoreSummary, CategoryTestSessionScoreSummary, CCSessionScoreSummary
)

admin.site.register(GroupTest)
admin.site.register(GroupTestCategory)
admin.site.register(EasyQuestion)
admin.site.register(MediumQuestion)
admin.site.register(HardQuestion)
admin.site.register(ChoiceForEasyQ)
admin.site.register(ChoiceForMediumQ)
admin.site.register(ChoiceForHardQ)
admin.site.register(GroupTestCombinedCategory)
admin.site.register(SubTestSessionPassword)
admin.site.register(CategoryTestSession)
admin.site.register(CategorySessionPassword)
admin.site.register(CombinedCategoryTestSession)
admin.site.register(CombinedCategorySessionPassword)
admin.site.register(SubTestSession)
admin.site.register(GroupTestMarksLibrary)
admin.site.register(CombinedGroupTestMarksLibrary)
admin.site.register(SubTestsMarksLibrary)
admin.site.register(SubTestSessionScoreSummary)
admin.site.register(CategoryTestSessionScoreSummary)
admin.site.register(CCSessionScoreSummary)




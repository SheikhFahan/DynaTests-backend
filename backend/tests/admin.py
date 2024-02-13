from django.contrib import admin

# Register your models here.
from .models import Test, Category, EasyQuestion, MediumQuestion, HardQuestion, ChoiceForEasyQ ,ChoiceForMediumQ, ChoiceForHardQ, CombinedTestCategory

admin.site.register(Test)
admin.site.register(Category)
admin.site.register(EasyQuestion)
admin.site.register(MediumQuestion)
admin.site.register(HardQuestion)
admin.site.register(ChoiceForEasyQ)
admin.site.register(ChoiceForMediumQ)
admin.site.register(ChoiceForHardQ)
admin.site.register(CombinedTestCategory)


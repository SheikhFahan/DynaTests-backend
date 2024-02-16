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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    def __str__(self):
        return self.name

class EasyQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null = True, blank = True, default= 'Coding')

    def save(self, *args, **kwargs):
        self.category = self.test.category
        super().save(*args, **kwargs)

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
    user = models.ForeignKey(User, on_delete = models.PROTECT)
    name = models.CharField(max_length= 100)
    associated_categories = models.ManyToManyField(Category)
    description = models.CharField(max_length = 100, default = "Defalult Description a quick brown fox jumps over a lazy dog.")


    def get_username(self):
        return  str(self.user.username)

    def __str__(self) -> str:
        return self.name
    

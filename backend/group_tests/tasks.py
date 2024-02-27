from celery import shared_task

from django.contrib.auth.models import User
from django.db.models import Avg

from .models import (
    SubTestsMarksLibrary, SubTestSession, SubTestSessionScoreSummary,
    GroupTestMarksLibrary, CategoryTestSession, CategoryTestSessionScoreSummary,
    CombinedGroupTestMarksLibrary, CombinedCategoryTestSession, CCSessionScoreSummary
)

@shared_task
def add_subtest_session_summary( **kwargs):
    session = kwargs.get('session')
    institute = kwargs.get('institute')
    session = SubTestSession.objects.get(pk = session)
    institute_obj = User.objects.get(pk  = institute)
    avg_score = SubTestsMarksLibrary.objects.filter(institute = institute_obj, session = 4).aggregate(Avg('score'))['score__avg']
    SubTestSessionScoreSummary.objects.create(institute = institute_obj, session  = session, score = avg_score)

@shared_task
def add_category_test_session_summary( **kwargs):
    session = kwargs.get('session')
    institute = kwargs.get('institute')
    session = CategoryTestSession.objects.get(pk = session)
    institute_obj = User.objects.get(pk  = institute)
    avg_score = GroupTestMarksLibrary.objects.filter(institute = institute_obj, session = 3).aggregate(Avg('score'))['score__avg']
    CategoryTestSessionScoreSummary.objects.create(institute = institute_obj, session  = session, score = avg_score)

@shared_task
def add_cc_session_summary( **kwargs):
    session = kwargs.get('session')
    institute = kwargs.get('institute')
    session = CombinedCategoryTestSession.objects.get(pk = session)
    institute_obj = User.objects.get(pk  = institute)
    avg_score = CombinedGroupTestMarksLibrary.objects.filter(institute = institute_obj, session = 6).aggregate(Avg('score'))['score__avg']
    CCSessionScoreSummary.objects.create(institute = institute_obj, session  = session, score = avg_score)
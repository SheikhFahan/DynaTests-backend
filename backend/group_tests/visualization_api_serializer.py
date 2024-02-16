from rest_framework import serializers


class QuestionsDataSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    category_name = serializers.CharField(max_length = 100)
    count  = serializers.IntegerField()

class QuestionsDataDetailSerializer(serializers.Serializer):
    """"
    gives the total number of question per category/subtest/cc for all of them for  a user
    """
    name = serializers.CharField(max_length = 100)
    total_easy = serializers.IntegerField()
    total_medium = serializers.IntegerField()
    total_hard= serializers.IntegerField()

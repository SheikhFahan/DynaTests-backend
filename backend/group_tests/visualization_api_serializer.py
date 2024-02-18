from rest_framework import serializers


class QuestionsDataSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    category_name = serializers.CharField(max_length = 100)
    count  = serializers.IntegerField(required = False)

class CCDataSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    category_name = serializers.CharField(max_length = 100)
    associated_categories_list  = serializers.CharField()

class QuestionsDataDetailSerializer(serializers.Serializer):
    """"
    gives the total number of question per category/subtest/cc for all of them for  a user
    """
    # pk for category not for the model
    test_pk = serializers.IntegerField(required = False)
    category_pk = serializers.IntegerField()
    category_name = serializers.CharField(max_length = 100)
    total_easy = serializers.IntegerField()
    total_medium = serializers.IntegerField()
    total_hard= serializers.IntegerField()

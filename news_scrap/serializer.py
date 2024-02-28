from rest_framework import serializers
from .models import *

class SourceSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=255)
    url=serializers.URLField()
    title=serializers.CharField(max_length=255)

class NewsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    image_url = serializers.URLField()
    content=serializers.CharField()
    sources=SourceSerializer(many=True, read_only=True)
    day=serializers.IntegerField()
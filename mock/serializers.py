from rest_framework import serializers
from .models import Page

class PageSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        assert type(instance) is Page
        return instance.name
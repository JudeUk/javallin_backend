from rest_framework import serializers
from .models import Case

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'

class CaseDataSerializer(serializers.Serializer):
    class Meta:
        model = Case
        fields =  ('facts', 'arguments', 'reference_materials','issues')

def create(validated_data):
        """
        Create and return a new `Case` instance, given the validated data.
        """
        return Case.objects.create(**validated_data)
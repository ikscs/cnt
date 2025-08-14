from rest_framework import serializers
from .models import Balance, TestOrder

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'

class TestOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestOrder
        fields = '__all__'

from rest_framework import serializers
from .models import Balance, TestOrder, SubscriptionBasePrice, Order, CameraCategory

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'

class TestOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestOrder
        fields = '__all__'

class SubscriptionBasePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionBasePrice
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class CameraCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraCategory
        fields = '__all__'

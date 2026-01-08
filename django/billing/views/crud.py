from rest_framework import viewsets

from pcnt.base import PCNTBaseViewSet, PCNTBaseReadOnlyViewSet

from ..models import Balance
from ..serializers import BalanceSerializer
class BalanceViewSet(PCNTBaseViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer

from ..models import TestOrder
from ..serializers import TestOrderSerializer
class TestOrderViewSet(viewsets.ModelViewSet):
    queryset = TestOrder.objects.all()
    serializer_class = TestOrderSerializer

from ..models import SubscriptionBasePrice
from ..serializers import SubscriptionBasePriceSerializer
class SubscriptionBasePriceViewSet(PCNTBaseReadOnlyViewSet):
    queryset = SubscriptionBasePrice.objects.all()
    serializer_class = SubscriptionBasePriceSerializer

from ..models import Order
from ..serializers import OrderSerializer
class OrderReadOnlyViewSet(PCNTBaseReadOnlyViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

from ..models import CameraCategory
from ..serializers import CameraCategorySerializer
class CameraCategoryReadOnlyViewSet(PCNTBaseReadOnlyViewSet):
    queryset = CameraCategory.objects.all()
    serializer_class = CameraCategorySerializer

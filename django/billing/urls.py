from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PayView, PayCallbackView, PaymentLiqpayView, PaymentStatusView, PaymentResultView, BalanceViewSet

router = DefaultRouter()
router.register(r'balance', BalanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pay/', PayView.as_view(), name='pay'),
    path('pay_callback/', PayCallbackView.as_view(), name='pay_callback'),
    path('pay_status/', PaymentStatusView.as_view(), name='pay_status'),
    path('pay_result/', PaymentResultView.as_view(), name='pay_result'),
    path('pay_liqpay/', PaymentLiqpayView.as_view(), name='pay_liqpay'),
]


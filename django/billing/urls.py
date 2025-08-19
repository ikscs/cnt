from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PayView, PayCallbackView, PaymentLiqpayView, PaymentStatusView, PaymentResultView, CreateLiqpayOrderView
from .views import BalanceViewSet, TestOrderViewSet, SubscriptionBasePriceViewSet

router = DefaultRouter()
router.register(r'balance', BalanceViewSet)
router.register(r'test_order', TestOrderViewSet)
router.register(r'subscription_base_price', SubscriptionBasePriceViewSet, basename='subscriptionbaseprice')

urlpatterns = [
    path('', include(router.urls)),
    path('pay/', PayView.as_view(), name='pay'),
    path('pay_callback/', PayCallbackView.as_view(), name='pay_callback'),
    path('pay_status/', PaymentStatusView.as_view(), name='pay_status'),
    path('pay_result/', PaymentResultView.as_view(), name='pay_result'),
    path('pay_liqpay/', PaymentLiqpayView.as_view(), name='pay_liqpay'),

    path('create_liqpay_order/', CreateLiqpayOrderView.as_view(), name='create_liqpay_order'),
]

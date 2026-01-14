from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter

from pcnt.views import CallDbFunctionView
from pcnt.views import CallReportView
from pcnt.views import RegisterCustomerView

from .views import HelloView
from .views import UnsubscribeView

from pcnt.views import ThemeViewSet
router_api = DefaultRouter()
router_api.register(r'theme', ThemeViewSet)

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/f5", CallDbFunctionView.as_view(), name='call-db-function'),
    path("api/report/", CallReportView.as_view(), name='call-report-view'),

    path("api/register_customer/", RegisterCustomerView.as_view(), name='register_customer'),
    path("api/", include(router_api.urls)),

    path("api/hello/", HelloView.as_view(), name='hello'),
    path('api/authdemo/', include('authdemo.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/unsubscribe/", UnsubscribeView.as_view(), name='unsubscribe'),
]

urlpatterns.append(path('api/pcnt/', include('pcnt.urls')))
urlpatterns.append(path('api/billing/', include('billing.urls')))

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

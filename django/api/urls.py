from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter
from pcnt.views import AgeViewSet, AppViewSet, BillingViewSet, BillingCostViewSet, BillingIncomeViewSet, CityViewSet, CountryViewSet, CustomerViewSet, CustomerToAppViewSet, DivisionViewSet, EventCrosslineViewSet, EventDataViewSet, FaceDataViewSet, FaceRefererDataViewSet, FaceTimeSlotViewSet, FormViewSet, FormDataViewSet, FormTagViewSet, FormVersionViewSet, IncomingViewSet, ManagerOrderViewSet, MethodViewSet, OriginViewSet, OriginScheduleViewSet, OriginTypeViewSet, OsdViewSet, PermReportViewSet, PersonViewSet, PersonGroupViewSet, PointViewSet
from pcnt.views import ParamViewSet
from pcnt.views import HostContainerStatusViewSet, HostDiskUsageViewSet
from pcnt.views import MetricViewSet, MetricHistoryViewSet

from pcnt.views import LatestMetricViewSet

router_pcnt = DefaultRouter()

router_pcnt.register(r'age', AgeViewSet)
router_pcnt.register(r'app', AppViewSet)
router_pcnt.register(r'billing', BillingViewSet)
router_pcnt.register(r'billing_cost', BillingCostViewSet)
router_pcnt.register(r'billing_income', BillingIncomeViewSet)
router_pcnt.register(r'city', CityViewSet)
router_pcnt.register(r'country', CountryViewSet)
router_pcnt.register(r'customer', CustomerViewSet)
router_pcnt.register(r'customer_to_app', CustomerToAppViewSet)
router_pcnt.register(r'division', DivisionViewSet)
router_pcnt.register(r'event_crossline', EventCrosslineViewSet)
router_pcnt.register(r'event_data', EventDataViewSet)
router_pcnt.register(r'face_data', FaceDataViewSet)
router_pcnt.register(r'face_referer_data', FaceRefererDataViewSet)
router_pcnt.register(r'face_time_slot', FaceTimeSlotViewSet)
router_pcnt.register(r'form', FormViewSet)
router_pcnt.register(r'form_data', FormDataViewSet)
router_pcnt.register(r'form_tag', FormTagViewSet)
router_pcnt.register(r'form_version', FormVersionViewSet)
router_pcnt.register(r'incoming', IncomingViewSet)
router_pcnt.register(r'manager_order', ManagerOrderViewSet)
router_pcnt.register(r'method', MethodViewSet)
router_pcnt.register(r'origin', OriginViewSet)
router_pcnt.register(r'origin_schedule', OriginScheduleViewSet)
router_pcnt.register(r'origin_type', OriginTypeViewSet)
router_pcnt.register(r'osd', OsdViewSet)
router_pcnt.register(r'perm_report', PermReportViewSet)
router_pcnt.register(r'person', PersonViewSet)
router_pcnt.register(r'person_group', PersonGroupViewSet)
router_pcnt.register(r'point', PointViewSet)
router_pcnt.register(r'param', ParamViewSet)
router_pcnt.register(r'host_container_status', HostContainerStatusViewSet)
router_pcnt.register(r'host_disk_usage', HostDiskUsageViewSet)
router_pcnt.register(r'metric', MetricViewSet)
router_pcnt.register(r'metric_history', MetricHistoryViewSet)
router_pcnt.register(r'v_metric_last', LatestMetricViewSet)

from pcnt.views import FaceRefererByPerson

from .views import CallDbFunctionView
from .views import HelloView

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/pcnt/", include(router_pcnt.urls)),
    path("api/f5", CallDbFunctionView.as_view(), name='call-db-function'),
    path("api/hello/", HelloView.as_view(), name='hello'),
    path('api/authdemo/', include('authdemo.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#    path('api/pcnt/faces/person/<int:person_id>/', FaceRefererByPerson.as_view(), name='faces-by-person'),
    path('api/pcnt/face_referer_data/person/<int:person_id>/', FaceRefererByPerson.as_view(), name='faces-by-person'),
#    path("api/", include("helloworld.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

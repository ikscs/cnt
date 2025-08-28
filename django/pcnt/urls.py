from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AgeViewSet, AppViewSet, BillingViewSet, BillingCostViewSet, BillingIncomeViewSet, CityViewSet, CountryViewSet, CustomerViewSet, CustomerToAppViewSet, DivisionViewSet, EventCrosslineViewSet, EventDataViewSet, FaceDataViewSet, FaceRefererDataViewSet, FaceTimeSlotViewSet, FormViewSet, FormDataViewSet, FormTagViewSet, FormVersionViewSet, IncomingViewSet, ManagerOrderViewSet, MethodViewSet, OriginViewSet, OriginTypeViewSet, OsdViewSet, PermReportViewSet, PersonViewSet, PersonGroupViewSet, PointViewSet
from .views import ParamViewSet
from .views import HostContainerStatusViewSet, HostDiskUsageViewSet
from .views import MetricViewSet, MetricHistoryViewSet

from .views import LatestMetricViewSet
from .views import ExportVCAViewSet

from .views import FaceRefererByPerson
from .views import FaceRefererViewSet
from .views import VCustomerOriginViewSet
from .views import VCustomerPersonViewSet
from .views import VCustomerExportViewSet
from .views import UserCacheViewSet
from .views import OriginByPointId
from .views import ReportScheduleViewSet
from .views import VReportScheduleViewSet

from .views import ExportVCAViewSetByPoint

from .views import VReportView

router = DefaultRouter()
router.register(r'age', AgeViewSet)
router.register(r'app', AppViewSet)
router.register(r'billing', BillingViewSet)
router.register(r'billing_cost', BillingCostViewSet)
router.register(r'billing_income', BillingIncomeViewSet)
router.register(r'city', CityViewSet)
router.register(r'country', CountryViewSet)
router.register(r'customer', CustomerViewSet)
router.register(r'customer_to_app', CustomerToAppViewSet)
router.register(r'division', DivisionViewSet)
router.register(r'event_crossline', EventCrosslineViewSet)
router.register(r'event_data', EventDataViewSet)
router.register(r'face_data', FaceDataViewSet)
router.register(r'face_referer_data', FaceRefererDataViewSet)
router.register(r'face_time_slot', FaceTimeSlotViewSet)
router.register(r'form', FormViewSet)
router.register(r'form_data', FormDataViewSet)
router.register(r'form_tag', FormTagViewSet)
router.register(r'form_version', FormVersionViewSet)
router.register(r'incoming', IncomingViewSet)
router.register(r'manager_order', ManagerOrderViewSet)
router.register(r'method', MethodViewSet)
router.register(r'origin', OriginViewSet)
router.register(r'origin_type', OriginTypeViewSet)
router.register(r'osd', OsdViewSet)
router.register(r'person', PersonViewSet)
router.register(r'person_group', PersonGroupViewSet)
router.register(r'point', PointViewSet)
router.register(r'param', ParamViewSet)
router.register(r'host_container_status', HostContainerStatusViewSet)
router.register(r'host_disk_usage', HostDiskUsageViewSet)
router.register(r'metric', MetricViewSet)
router.register(r'metric_history', MetricHistoryViewSet)
router.register(r'v_metric_last', LatestMetricViewSet)
router.register(r'v_export_vca', ExportVCAViewSet)

router.register(r'v_customer_origin', VCustomerOriginViewSet, basename='v-customer-origin')
router.register(r'v_customer_person', VCustomerPersonViewSet, basename='v-customer-person')
router.register(r'v_customer_export', VCustomerExportViewSet, basename='v-customer-export')
router.register(r'user_cache', UserCacheViewSet)
router.register(r'report_schedule', ReportScheduleViewSet)
router.register(r'v_report_schedule', VReportScheduleViewSet)

perm_report_list = PermReportViewSet.as_view({'get': 'list', 'post': 'create',})
perm_report_detail = PermReportViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',})

urlpatterns = [
    path('', include(router.urls)),

    path('face_referer_data/person/<int:person_id>/', FaceRefererByPerson.as_view(), name='faces-by-person'),
    path('v_export_vca/point/<int:point_id>/', ExportVCAViewSetByPoint.as_view(), name='v_export_vca-by-point'),
    path('origin/point/<int:point_id>/', OriginByPointId.as_view(), name='origin-by-point'),
    path('perm_report/', perm_report_list, name='perm_report-list'),
    path('perm_report/<str:app_id>/<int:report_id>/', perm_report_detail, name='perm_report-detail'),

    path("v_perm_report/", VReportView.as_view(), name='v_report_view'),
]

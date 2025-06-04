from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from rest_framework.routers import DefaultRouter
from pcnt.views import AgeViewSet, AppViewSet, BillingViewSet, BillingCostViewSet, BillingIncomeViewSet, CityViewSet, CountryViewSet, CustomerViewSet, CustomerToAppViewSet, DivisionViewSet, EventCrosslineViewSet, EventDataViewSet, FaceDataViewSet, FaceRefererDataViewSet, FaceTimeSlotViewSet, FormViewSet, FormDataViewSet, FormTagViewSet, FormVersionViewSet, IncomingViewSet, ManagerOrderViewSet, MethodViewSet, OriginViewSet, OriginScheduleViewSet, OriginTypeViewSet, OsdViewSet, PermReportViewSet, PersonViewSet, PersonGroupViewSet, PointViewSet

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

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/pcnt/", include(router_pcnt.urls)),
    path("api/", include("helloworld.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

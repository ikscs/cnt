#views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Age, App, Billing, BillingCost, BillingIncome, City, Country, Customer, CustomerToApp, Division, EventCrossline, EventData, FaceData, FaceRefererData, FaceTimeSlot, Form, FormData, FormTag, FormVersion, Incoming, ManagerOrder, Method, Origin, OriginSchedule, OriginType, Osd, PermReport, Person, PersonGroup, Point
from .serializers import AgeSerializer, AppSerializer, BillingSerializer, BillingCostSerializer, BillingIncomeSerializer, CitySerializer, CountrySerializer, CustomerSerializer, CustomerToAppSerializer, DivisionSerializer, EventCrosslineSerializer, EventDataSerializer, FaceDataSerializer, FaceRefererDataSerializer, FaceTimeSlotSerializer, FormSerializer, FormDataSerializer, FormTagSerializer, FormVersionSerializer, IncomingSerializer, ManagerOrderSerializer, MethodSerializer, OriginSerializer, OriginScheduleSerializer, OriginTypeSerializer, OsdSerializer, PermReportSerializer, PersonSerializer, PersonGroupSerializer, PointSerializer

class AgeViewSet(viewsets.ModelViewSet):
    queryset = Age.objects.all()
    serializer_class = AgeSerializer

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer

class BillingViewSet(viewsets.ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer

class BillingCostViewSet(viewsets.ModelViewSet):
    queryset = BillingCost.objects.all()
    serializer_class = BillingCostSerializer

class BillingIncomeViewSet(viewsets.ModelViewSet):
    queryset = BillingIncome.objects.all()
    serializer_class = BillingIncomeSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerToAppViewSet(viewsets.ModelViewSet):
    queryset = CustomerToApp.objects.all()
    serializer_class = CustomerToAppSerializer

class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

class EventCrosslineViewSet(viewsets.ModelViewSet):
    queryset = EventCrossline.objects.all()
    serializer_class = EventCrosslineSerializer

class EventDataViewSet(viewsets.ModelViewSet):
    queryset = EventData.objects.all()
    serializer_class = EventDataSerializer

class FaceDataViewSet(viewsets.ModelViewSet):
    queryset = FaceData.objects.all()
    serializer_class = FaceDataSerializer

class FaceRefererDataViewSet(viewsets.ModelViewSet):
    queryset = FaceRefererData.objects.all()
    serializer_class = FaceRefererDataSerializer

class FaceRefererByPerson(APIView):
    def get(self, request, person_id):
        faces = FaceRefererData.objects.filter(person_id=person_id)
        serializer = FaceRefererDataSerializer(faces, many=True)
        return Response(serializer.data)

class FaceTimeSlotViewSet(viewsets.ModelViewSet):
    queryset = FaceTimeSlot.objects.all()
    serializer_class = FaceTimeSlotSerializer

class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer

class FormDataViewSet(viewsets.ModelViewSet):
    queryset = FormData.objects.all()
    serializer_class = FormDataSerializer

class FormTagViewSet(viewsets.ModelViewSet):
    queryset = FormTag.objects.all()
    serializer_class = FormTagSerializer

class FormVersionViewSet(viewsets.ModelViewSet):
    queryset = FormVersion.objects.all()
    serializer_class = FormVersionSerializer

class IncomingViewSet(viewsets.ModelViewSet):
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer

class ManagerOrderViewSet(viewsets.ModelViewSet):
    queryset = ManagerOrder.objects.all()
    serializer_class = ManagerOrderSerializer

class MethodViewSet(viewsets.ModelViewSet):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer

class OriginViewSet(viewsets.ModelViewSet):
    queryset = Origin.objects.all()
    serializer_class = OriginSerializer

class OriginScheduleViewSet(viewsets.ModelViewSet):
    queryset = OriginSchedule.objects.all()
    serializer_class = OriginScheduleSerializer

class OriginTypeViewSet(viewsets.ModelViewSet):
    queryset = OriginType.objects.all()
    serializer_class = OriginTypeSerializer

class OsdViewSet(viewsets.ModelViewSet):
    queryset = Osd.objects.all()
    serializer_class = OsdSerializer

class PermReportViewSet(viewsets.ModelViewSet):
    queryset = PermReport.objects.all()
    serializer_class = PermReportSerializer

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

class PersonGroupViewSet(viewsets.ModelViewSet):
    queryset = PersonGroup.objects.all()
    serializer_class = PersonGroupSerializer

class PointViewSet(viewsets.ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer

from .models import Param

from .serializers import ParamSerializer
from rest_framework.permissions import IsAuthenticated

#class ParamViewSet(viewsets.ModelViewSet):
#    queryset = Param.objects.all()
#    serializer_class = ParamSerializer

class ParamViewSet(viewsets.ModelViewSet):
    queryset = Param.objects.all()
    serializer_class = ParamSerializer
    permission_classes = [IsAuthenticated]

from .models import HostContainerStatus, HostDiskUsage
from .serializers import HostContainerStatusSerializer, HostDiskUsageSerializer

class HostContainerStatusViewSet(viewsets.ModelViewSet):
    queryset = HostContainerStatus.objects.all()
    serializer_class = HostContainerStatusSerializer

class HostDiskUsageViewSet(viewsets.ModelViewSet):
    queryset = HostDiskUsage.objects.all()
    serializer_class = HostDiskUsageSerializer

from .models import Metric, MetricHistory
from .serializers import MetricSerializer, MetricHistorySerializer

class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer

class MetricHistoryViewSet(viewsets.ModelViewSet):
    queryset = MetricHistory.objects.all()
    serializer_class = MetricHistorySerializer

from .models import LatestMetric
from .serializers import LatestMetricSerializer

class LatestMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LatestMetric.objects.all()
    serializer_class = LatestMetricSerializer

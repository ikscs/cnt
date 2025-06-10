#serializers.py
from rest_framework import serializers

from .models import Age, App, Billing, BillingCost, BillingIncome, City, Country, Customer, CustomerToApp, Division, EventCrossline, EventData, FaceData, FaceRefererData, FaceTimeSlot, Form, FormData, FormTag, FormVersion, Incoming, ManagerOrder, Method, Origin, OriginSchedule, OriginType, Osd, PermReport, Person, PersonGroup, Point

class AgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Age
        fields = '__all__'

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = '__all__'

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = '__all__'

class BillingCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingCost
        fields = '__all__'

class BillingIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingIncome
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class CustomerToAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerToApp
        fields = '__all__'

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'

class EventCrosslineSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCrossline
        fields = '__all__'

class EventDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventData
        fields = '__all__'

class FaceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceData
        fields = '__all__'

class FaceRefererDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceRefererData
        fields = '__all__'

class FaceTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceTimeSlot
        fields = '__all__'

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = '__all__'
        read_only_fields = ['id']

class FormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormData
        fields = '__all__'

class FormTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTag
        fields = '__all__'

class FormVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormVersion
        fields = '__all__'

class IncomingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming
        fields = '__all__'

class ManagerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerOrder
        fields = '__all__'

class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = '__all__'

class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = '__all__'

class OriginScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginSchedule
        fields = '__all__'

class OriginTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginType
        fields = '__all__'

class OsdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Osd
        fields = '__all__'

class PermReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermReport
        fields = '__all__'

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class PersonGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonGroup
        fields = '__all__'

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'

from .models import Param

class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = '__all__'

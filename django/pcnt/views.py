#views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from rest_framework import status
from django.db import connections
from django.utils.html import escape  # for sanitizing 'func' input
import json
import requests
from decimal import Decimal
from datetime import date, datetime

from django_filters.rest_framework import DjangoFilterBackend

from .base import PCNTBaseViewSet, PCNTBaseAPIView, PCNTBaseActionViewSet, PCNTBaseReadOnlyViewSet, PCNTBaseNoPkViewSet

from .models import Age, App, Billing, BillingCost, BillingIncome, City, Country, Customer, CustomerToApp, Division, EventCrossline, EventData, FaceData, FaceRefererData, FaceTimeSlot, Form, FormData, FormTag, FormVersion, Incoming, ManagerOrder, Method, Origin, OriginType, Osd, PermReport, Person, PersonGroup, Point
from .serializers import AgeSerializer, AppSerializer, BillingSerializer, BillingCostSerializer, BillingIncomeSerializer, CitySerializer, CountrySerializer, CustomerSerializer, CustomerToAppSerializer, DivisionSerializer, EventCrosslineSerializer, EventDataSerializer, FaceDataSerializer, FaceRefererDataSerializer, FaceTimeSlotSerializer, FormSerializer, FormDataSerializer, FormTagSerializer, FormVersionSerializer, IncomingSerializer, ManagerOrderSerializer, MethodSerializer, OriginSerializer, OriginTypeSerializer, OsdSerializer, PermReportSerializer, PersonSerializer, PersonGroupSerializer, PointSerializer

class AgeViewSet(PCNTBaseViewSet):
    queryset = Age.objects.all()
    serializer_class = AgeSerializer

class AppViewSet(PCNTBaseViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer

class BillingViewSet(PCNTBaseViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer

class BillingCostViewSet(PCNTBaseViewSet):
    queryset = BillingCost.objects.all()
    serializer_class = BillingCostSerializer

class BillingIncomeViewSet(PCNTBaseViewSet):
    queryset = BillingIncome.objects.all()
    serializer_class = BillingIncomeSerializer

class CityViewSet(PCNTBaseViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CountryViewSet(PCNTBaseViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CustomerViewSet(PCNTBaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerToAppViewSet(PCNTBaseViewSet):
    queryset = CustomerToApp.objects.all()
    serializer_class = CustomerToAppSerializer

class DivisionViewSet(PCNTBaseViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

class EventCrosslineViewSet(PCNTBaseViewSet):
    queryset = EventCrossline.objects.all()
    serializer_class = EventCrosslineSerializer

class EventDataViewSet(PCNTBaseViewSet):
    queryset = EventData.objects.all()
    serializer_class = EventDataSerializer

class FaceDataViewSet(PCNTBaseViewSet):
    queryset = FaceData.objects.all()
    serializer_class = FaceDataSerializer

class FaceRefererDataViewSet(PCNTBaseViewSet):
    queryset = FaceRefererData.objects.all()
    serializer_class = FaceRefererDataSerializer

class FaceRefererByPerson(PCNTBaseAPIView):
    def get(self, request, person_id):
        faces = FaceRefererData.objects.filter(person_id=person_id)
        serializer = FaceRefererDataSerializer(faces, many=True)
        return Response(serializer.data)

class FaceRefererViewSet(PCNTBaseActionViewSet):
    @action(detail=True, methods=['get'], url_path='person')
    def by_person(self, request, pk=None):
        person_id = pk  # Since `detail=True`, `pk` comes from the URL
        faces = FaceRefererData.objects.filter(person_id=person_id)
        serializer = FaceRefererDataSerializer(faces, many=True)
        return Response(serializer.data)

class FaceTimeSlotViewSet(PCNTBaseViewSet):
    queryset = FaceTimeSlot.objects.all()
    serializer_class = FaceTimeSlotSerializer

class FormViewSet(PCNTBaseViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer

class FormDataViewSet(PCNTBaseViewSet):
    queryset = FormData.objects.all()
    serializer_class = FormDataSerializer

class FormTagViewSet(PCNTBaseViewSet):
    queryset = FormTag.objects.all()
    serializer_class = FormTagSerializer

class FormVersionViewSet(PCNTBaseViewSet):
    queryset = FormVersion.objects.all()
    serializer_class = FormVersionSerializer

class IncomingViewSet(PCNTBaseViewSet):
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer

class ManagerOrderViewSet(PCNTBaseViewSet):
    queryset = ManagerOrder.objects.all()
    serializer_class = ManagerOrderSerializer

class MethodViewSet(PCNTBaseViewSet):
    queryset = Method.objects.all()
    serializer_class = MethodSerializer

class OriginViewSet(PCNTBaseViewSet):
    queryset = Origin.objects.all()
    serializer_class = OriginSerializer

class OriginByPointId(PCNTBaseAPIView):
    def get(self, request, point_id):
        records = Origin.objects.filter(point_id=point_id)
        serializer = OriginSerializer(records, many=True)
        return Response(serializer.data)

class OriginTypeViewSet(PCNTBaseViewSet):
    queryset = OriginType.objects.all()
    serializer_class = OriginTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enabled',]

class OsdViewSet(PCNTBaseViewSet):
    queryset = Osd.objects.all()
    serializer_class = OsdSerializer

class PermReportViewSet(PCNTBaseNoPkViewSet):
    model_class = PermReport
    #queryset = PermReport.objects.all()
    serializer_class = PermReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['app_id', 'report_id']

class PersonViewSet(PCNTBaseViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

class PersonGroupViewSet(PCNTBaseViewSet):
    queryset = PersonGroup.objects.all()
    serializer_class = PersonGroupSerializer

class PointViewSet(PCNTBaseViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer

from .models import Param

from .serializers import ParamSerializer
#from rest_framework.permissions import IsAuthenticated

#class ParamViewSet(PCNTBaseViewSet):
#    queryset = Param.objects.all()
#    serializer_class = ParamSerializer

class ParamViewSet(PCNTBaseViewSet):
    queryset = Param.objects.all()
    serializer_class = ParamSerializer

from .models import HostContainerStatus, HostDiskUsage
from .serializers import HostContainerStatusSerializer, HostDiskUsageSerializer

class HostContainerStatusViewSet(PCNTBaseViewSet):
    queryset = HostContainerStatus.objects.all()
    serializer_class = HostContainerStatusSerializer

class HostDiskUsageViewSet(PCNTBaseViewSet):
    queryset = HostDiskUsage.objects.all()
    serializer_class = HostDiskUsageSerializer

from .models import Metric, MetricHistory
from .serializers import MetricSerializer, MetricHistorySerializer

class MetricViewSet(PCNTBaseViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer

class MetricHistoryViewSet(PCNTBaseViewSet):
    queryset = MetricHistory.objects.all()
    serializer_class = MetricHistorySerializer

from .models import LatestMetric
from .serializers import LatestMetricSerializer

class LatestMetricViewSet(PCNTBaseReadOnlyViewSet):
    queryset = LatestMetric.objects.all()
    serializer_class = LatestMetricSerializer
#    permission_classes = [IsAuthenticated]

from .models import ExportVCA
from .serializers import ExportVCASerializer

class ExportVCAViewSet(PCNTBaseReadOnlyViewSet):
    queryset = ExportVCA.objects.all()
    serializer_class = ExportVCASerializer

class ExportVCAViewSetByPoint(PCNTBaseAPIView):
    def get(self, request, point_id):
        data = ExportVCA.objects.filter(point_id=point_id)
        serializer = ExportVCASerializer(data, many=True)
        return Response(serializer.data)

from .models import VCustomerOrigin
from .serializers import VCustomerOriginSerializer
class VCustomerOriginViewSet(PCNTBaseReadOnlyViewSet):
    queryset = VCustomerOrigin.objects.all()
    serializer_class = VCustomerOriginSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['point_id',]

from .models import VCustomerPerson
from .serializers import VCustomerPersonSerializer
class VCustomerPersonViewSet(PCNTBaseReadOnlyViewSet):
    queryset = VCustomerPerson.objects.all()
    serializer_class = VCustomerPersonSerializer

from .models import VCustomerExport
from .serializers import VCustomerExportSerializer
class VCustomerExportViewSet(PCNTBaseReadOnlyViewSet):
    queryset = VCustomerExport.objects.all()
    serializer_class = VCustomerExportSerializer

from .models import UserCache
from .serializers import UserCacheSerializer
class UserCacheViewSet(PCNTBaseViewSet):
    queryset = UserCache.objects.all()
    serializer_class = UserCacheSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_id', 'tenant_id', 'mode']

from .models import Theme
from .serializers import ThemeSerializer
class ThemeViewSet(PCNTBaseViewSet):
    queryset = Theme.objects.order_by('sortord')
    serializer_class = ThemeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['app_id', 'enabled']

from .models import ReportSchedule
from .serializers import ReportScheduleSerializer
class ReportScheduleViewSet(PCNTBaseViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer

from .models import VReportSchedule
from .serializers import VReportScheduleSerializer
class VReportScheduleViewSet(PCNTBaseReadOnlyViewSet):
    queryset = VReportSchedule.objects.all()
    serializer_class = VReportScheduleSerializer

class CallDbFunctionView(PCNTBaseAPIView):
    def post(self, request):
        func = request.query_params.get("func")
        lang = request.query_params.get('lang', 'uk')

        if not func:
            return Response({"error": "Missing 'func' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            escaped_func = escape(func)  # basic sanitization
            input_data = json.dumps(request.data)

            with connections['pcnt'].cursor() as cursor:
                query = "SET app.lang = %s;"
                cursor.execute(query, [lang])

                query = f"SELECT {escaped_func}(%s);"
                cursor.execute(query, [input_data])
                rows = cursor.fetchall()

            result = [json.loads(row[0]) for row in rows]

            return Response(*result, content_type='application/json')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def custom_encoder(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, datetime):
        return json.dumps(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

class CallReportView(PCNTBaseAPIView):
    def commot_t(self, cursor, key):
        query = f"SELECT common_t(%s);"
        cursor.execute(query, [key])
        rows = cursor.fetchall()
        if not rows:
            return key
        return rows[0][0]

    def post(self, request):
        with connections['pcnt'].cursor() as cursor:
            lang = request.data.get('lang', 'uk')
            query = "SET app.lang = %s"
            cursor.execute(query, [lang])

            query = "SELECT query, report_config, report_name, report_name_lang, report_column  FROM v_perm_report WHERE app_id=%s AND report_id=%s AND lang=%s;"
            cursor.execute(query, [request.data.get('app_id'), request.data.get('report_id'), lang])
            row = cursor.fetchone()
            if not row:
                return Response('Wrong report', status=status.HTTP_400_BAD_REQUEST)

            report_name = row[3] if row[3] else row[2]

            try:
                query = row[0]
                report_config = json.loads(row[1])
                report_column = json.loads(row[4]) if row[4] else None
            except Exception as err:
                return Response({'ok': False, 'data': [str(err)]}, content_type='application/json', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            required_params = set()
            for param in report_config['params']:
                required_params.add(param['name'])
                query = query.replace(f":{param['name']}", f"%({param['name']})s")

            val = {e.get('name'): e.get('value') for e in request.data.get('parameters') if e.get('name') in required_params}

            if set(val.keys()) != required_params:
                return Response({'ok': False, 'data': ['Incomplete parameters']}, content_type='application/json')

            data = []
            cursor.execute(query, val)
            field_names = [e[0] for e in cursor.description]

            if report_column:
                #print(report_column, type(report_column))
                column_dict = {r['field']: r['display'] for r in report_column}
                field_names_new = [column_dict.get(e, e) for e in field_names]
                field_names = field_names_new

            for row in cursor.fetchall():
                r = {name: value for name, value in zip(field_names, row)}
                data.append(r)

            recipient = request.data.get('recipient', None)
            if recipient:
                #Translate chart labels
                chart = report_config.get('chart', dict())
                for k, v in chart.items():
                    if 'label' in k:
                        chart[k] = self.commot_t(cursor, v)

#        recipient = request.data.get('recipient', None)
        if recipient:
            payload = {'recipient': recipient, 'subject': report_name, 'data': json.dumps(data, default=custom_encoder), 'chart': json.dumps(chart, default=custom_encoder)}
            requests.post('http://manager:8000/send_mail.json', data=payload)

        return Response({'ok': True, 'data': data}, content_type='application/json')

class VReportView(PCNTBaseAPIView):
    def load_vocabl(self, row, col, key='name'):
        #Load dictionary from col
        try:
            var_list = row[col]
        except Exception as err:
            return dict()

        if not var_list:
            return dict()

        if isinstance(var_list, str):
            try:
                var_list = json.loads(var_list)
            except Exception as err:
                return dict()

        if not isinstance(var_list, list):
            return dict()

        vocabl = dict()
        for var in var_list:
            name = var.get(key)
            if not name:
                continue
            vocabl[name] = dict()
            for k, v in var.items():
                if k == key:
                    continue
                vocabl[name][k] = v
        return vocabl

    def translate_data(self, report_config, params, vocabl, key='name'):
        data = report_config.get(params, [])
        data_new = []
        for var in data:
            name = var.get(key)
            if name and (name in vocabl):
                for k, v in vocabl[name].items():
                    if k in var:
                        var[k] = v
            data_new.append(var)
        return data_new

    def commot_t(self, cursor, key):
        query = f"SELECT common_t(%s);"
        cursor.execute(query, [key])
        rows = cursor.fetchall()
        if not rows:
            return key
        return rows[0][0]

    def get(self, request):
        data = request.query_params

        par = dict()
        for k in ['app_id', 'report_id', 'lang', 'tag']:
            v = data.get(k)
            if v:
                par[k] = v
        if par:
            query_par = '=%s AND '.join(par.keys())
            query_par = f' WHERE {query_par}=%s'
            query_par = query_par.replace('tag=%s', 'check_report_tag(%s, tag)')
        else:
            query_par = ''

        with connections['pcnt'].cursor() as cursor:
            query = "SET app.lang = %s"
            cursor.execute(query, [par.get('lang', 'uk')])

            query = f"SELECT * FROM v_perm_report{query_par};"
            cursor.execute(query, list(par.values()))
            field_names = [e[0] for e in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                return Response('Wrong report', status=status.HTTP_400_BAD_REQUEST)

            data = []
            for row in rows:
                #Load row into dict
                r = {name: value for name, value in zip(field_names, row)}

                #Get report_config
                try:
                    report_config = json.loads(r['report_config'])
                except Exception as err:
                    report_config = dict()

                #Replace report config with translated data params
                vocabl = self.load_vocabl(r, 'report_param')
                report_config['params'] = self.translate_data(report_config, 'params', vocabl)
                r.pop('report_param', None)

                #Replace report config with translated data columns
                vocabl = self.load_vocabl(r, 'report_column', key='field')
                report_config['columns'] = self.translate_data(report_config, 'columns', vocabl, key='field')
                r.pop('report_column', None)

                #Translate labels
                chart = report_config.get('chart')
                data_lists = (report_config['columns'], [chart]) if chart else (report_config['columns'],)
                for data_list in data_lists:
                    for row in data_list:
                        for k, v in row.items():
                            if 'label' in k:
                                row[k] = self.commot_t(cursor, v)

                r['report_config'] = json.dumps(report_config, ensure_ascii=False)

                #Translate name and description
                for k in field_names:
                    if k.endswith('_lang'):
                        if r[k]:
                            r[k.split('_lang')[0]] = r[k]
                        del r[k]
                data.append(r)

        return Response(data, content_type='application/json')

from .external_api import Userfront
class RegisterCustomerView(PCNTBaseAPIView):
    def post(self, request):
        try:
            user = request.user
            input_data = request.data
            data = [user.tenant_id, user.id, user.mode, input_data['legal_name'], input_data['address'], input_data['country'], input_data['city'], input_data['email']]
        except Exception as err:
            return Response('Wrong input data', status=status.HTTP_400_BAD_REQUEST)

        uf = Userfront(user)
        if uf.error:
            return Response(uf.error, status=status.HTTP_400_BAD_REQUEST)

        result = uf.set_roles(['admin', 'viewer'])
        if result != 'Ok':
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connections['pcnt'].cursor() as cursor:
                cursor.execute("SELECT register_customer(%s, %s, %s, %s, %s, %s, %s, %s);", data)
                row = cursor.fetchone()
                if not row:
                    return Response('Customer not created', status=status.HTTP_400_BAD_REQUEST)
                customer_id = row[0]
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

        result = uf.set_custom_data({'customer': customer_id})
#        if result != 'Ok':
#            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        data = {'customer_id': customer_id, 'legal_name': input_data['legal_name'], 'address': input_data['address'], 'country': input_data['country'], 'city': input_data['city'], 'email': input_data['email']}
        return Response(data, status=status.HTTP_201_CREATED)


class CheckConnectionView(PCNTBaseAPIView):
    def post(self, request):
        origin_type_id = request.data.get('origin_type_id')
        credentials = request.data.get('credentials')

        if not (origin_type_id and credentials):
            return Response({'success': False, 'description': 'origin_type_id or credentials missing'}, content_type='application/json')
        return self.check_connection(origin_id=None, origin_type_id=origin_type_id, credentials=json.dumps(credentials))

    def get(self, request):
        origin_id = request.query_params.get('origin_id')
        if not origin_id:
            return Response({'success': False, 'description': 'origin_id missing'}, content_type='application/json')
        return self.check_connection(origin_id=origin_id, origin_type_id=None, credentials=None)

    def check_connection(self, origin_id, origin_type_id, credentials):
        try:
            response = requests.post('http://camera_pooling:8000/check_connection.json', data={'origin_id': origin_id, 'origin_type_id': origin_type_id, 'credentials': credentials}, timeout=10)
            data = response.json()

            if response.status_code != 200:
                return Response({'success': False, 'description': 'backend error'}, content_type='application/json', status=response.status_code)

            return Response({'success': data['is_connected'], 'description': data['error_txt']}, content_type='application/json')

        except Exception as err:
            return Response({'success': False, 'description': str(err)}, content_type='application/json')

from django.db import models
from django.db.models import Value, Expression
from django.contrib.postgres.fields import ArrayField

class Age(models.Model):
    age_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    since = models.SmallIntegerField(blank=True, null=True)
    to = models.SmallIntegerField(blank=True, null=True)
    custormer = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'age'


class App(models.Model):
    app_id = models.TextField(primary_key=True)
    tenant_id = models.TextField()
    url = models.TextField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app'


class Billing(models.Model):
    customer_id = models.IntegerField(blank=True, null=True)
    balance = models.BigIntegerField(blank=True, null=True, db_comment='в копейках')

    class Meta:
        managed = False
        db_table = 'billing'


class BillingCost(models.Model):
    customer_id = models.IntegerField(blank=True, null=True)
    amount = models.BigIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    dt = models.DateTimeField(blank=True, null=True)
    type_service = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_cost'


class BillingIncome(models.Model):
    customer_id = models.IntegerField(blank=True, null=True)
    amount = models.BigIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    dt = models.DateTimeField(blank=True, null=True)
    type_pay = models.TextField(blank=True, null=True)
    acc = models.TextField(blank=True, null=True)
    payer = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_income'


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'city'


class Country(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=100)
    name_ml = models.JSONField()

    class Meta:
        managed = False
        db_table = 'country'


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    legal_name = models.TextField()
    address = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'


class CustomerToApp(models.Model):
    pk = models.CompositePrimaryKey('app_id', 'customer_id')
    customer_id = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customer_id', to_field='customer_id')
    app = models.ForeignKey(App, models.DO_NOTHING)
    child_tenant_id = models.TextField()
    is_active = models.BooleanField()
    paid = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_to_app'


class Division(models.Model):
    pk = models.CompositePrimaryKey('customer_id', 'division_id')
    customer_id = models.IntegerField()
    legal_name = models.TextField()
    address = models.TextField()
    division_id = models.TextField()

    class Meta:
        managed = False
        db_table = 'division'


class EventCrossline(models.Model):
    origin = models.ForeignKey('Origin', models.DO_NOTHING, db_column='origin', to_field='origin')
    ts = models.DateTimeField()
    prefix = models.CharField()
    name = models.CharField()
    origin_0 = models.ForeignKey('Origin', models.DO_NOTHING, db_column='origin_id', related_name='eventcrossline_origin_0_set')  # Field renamed because of name conflict.

    class Meta:
        managed = False
        db_table = 'event_crossline'
        unique_together = (('origin', 'ts', 'prefix', 'name', 'origin_0'),)


class EventData(models.Model):
    point_id = models.IntegerField(blank=True, null=True)
    dt = models.DateTimeField(blank=True, null=True)
    age = models.SmallIntegerField(blank=True, null=True)
    male = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_data'


class FaceData(models.Model):
    face_uuid = models.CharField(primary_key=True)
    file_uuid = models.CharField()
    face_idx = models.DecimalField(max_digits=20, decimal_places=0)
    ts = models.DateTimeField()
    embedding = models.TextField()  # This field type is a guess.
    facial_area = models.JSONField()
    confidence = models.FloatField()
    demography = models.JSONField(blank=True, null=True)
    time_slot = models.DateTimeField(blank=True, null=True)
    neighbors = models.TextField(blank=True, null=True)  # This field type is a guess.
    parent_uuid = models.CharField(blank=True, null=True)
    is_checked = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'face_data'


class FaceRefererData(models.Model):
    face_uuid = models.CharField(primary_key=True)
    photo = models.BinaryField()
    comment = models.TextField(blank=True, null=True)
    embedding = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    person_id = models.ForeignKey('Person', models.DO_NOTHING, db_column='person_id')
    sortord = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'face_referer_data'


class FaceTimeSlot(models.Model):
    ts_name = models.CharField(primary_key=True)
    func = models.CharField()
    comment = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'face_time_slot'


class Form(models.Model):
    id = models.UUIDField(primary_key=True, db_default=Value('gen_random_uuid()', output_field=models.UUIDField()), editable=False, db_comment='Уникальный идентификатор формы')
    name = models.CharField(max_length=255, db_comment='Название формы')
    description = models.TextField(blank=True, null=True, db_comment='Описание формы')
    category = models.TextField(db_comment='Категория формы')  # This field type is a guess.
    status = models.TextField(db_comment='Текущий статус формы')  # This field type is a guess.
    current_version = models.IntegerField(db_comment='Текущая версия формы')
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField()
    updated_by = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'form'
        db_table_comment = 'Основная таблица форм'


class FormData(models.Model):
    id = models.UUIDField(primary_key=True, db_default=Value('gen_random_uuid()', output_field=models.UUIDField()), editable=False,)
    form_id = models.ForeignKey(Form, models.DO_NOTHING, to_field='id', db_column='form_id', blank=True, null=True, unique=True)
    version = models.IntegerField()
    data = models.JSONField(db_comment='JSON данные, собранные через форму')
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField()
    updated_by = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'form_data'
        unique_together = (('id', 'version'),)
        db_table_comment = 'Данные, собранные через формы'

class FormTag(models.Model):
    pk = models.CompositePrimaryKey('form_id', 'tag')
    form_id = models.ForeignKey(Form, models.DO_NOTHING, to_field='id', db_column='form_id')
    tag = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'form_tag'
        db_table_comment = 'Теги для категоризации форм'

class FormVersion(models.Model):
    id = models.UUIDField(primary_key=True)
    form_id = models.ForeignKey(Form, models.DO_NOTHING, blank=True, null=True, to_field='id', db_column='form_id')
    version = models.IntegerField()
    config = models.JSONField(db_comment='JSON конфигурация формы, включая поля и макет')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'form_version'
        unique_together = (('form', 'version'),)
        db_table_comment = 'Версии форм с их конфигурацией'

class Incoming(models.Model):
    file_uuid = models.CharField(primary_key=True)
    ts = models.DateTimeField()
#    origin = models.ForeignKey('Origin', models.DO_NOTHING, db_column='origin', to_field='origin')
    title = models.CharField(blank=True, null=True)
    filename = models.CharField(blank=True, null=True)
    faces_cnt = models.SmallIntegerField(blank=True, null=True)
    origin_id = models.ForeignKey('Origin', models.DO_NOTHING, db_column='origin_id', to_field='id')#, 'related_name'='incoming_origin_0_set')  # Field renamed because of name conflict.

    class Meta:
        managed = False
        db_table = 'incoming'


class ManagerOrder(models.Model):
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    cmd = models.CharField()
    param = models.CharField(blank=True, null=True)
    return_code = models.IntegerField(blank=True, null=True)
    stdout = models.TextField(blank=True, null=True)
    stderr = models.TextField(blank=True, null=True)
    ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'manager_order'


class Method(models.Model):
    method_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    entry_point = models.CharField(max_length=255, blank=True, null=True)
    backend = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    face_detection_enabled = models.BooleanField()
    embedding_enabled = models.BooleanField()
    demography_enabled = models.BooleanField()
    param = models.JSONField(blank=True, null=True)
    max_distance = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'method'


class Origin(models.Model):
    origin = models.CharField(unique=True, max_length=255)
    point_id = models.ForeignKey('Point', models.DO_NOTHING, blank=True, null=True, db_column='point_id', to_field='point_id')
    origin_type_id = models.ForeignKey('OriginType', models.DO_NOTHING, db_column='origin_type_id', to_field='origin_type_id')
    credentials = models.JSONField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True)
    name = models.TextField(blank=True, null=True)
    face_width_px = models.SmallIntegerField(default=40)
    poling_period_s = models.IntegerField(default=180)

    class Meta:
        managed = False
        db_table = 'origin'
        unique_together = (('point', 'id'),)


class OriginType(models.Model):
    origin_type_id = models.AutoField(primary_key=True)
    name = models.CharField()
    protocol = models.CharField()
    vendor = models.CharField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    params = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField()
    template = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'origin_type'


class Osd(models.Model):
    origin_id = models.ForeignKey(Origin, models.DO_NOTHING, db_column='origin_id', to_field='id')
    header = models.CharField(blank=True, null=True)
    title = models.CharField()
    src_table = models.CharField()
    src_field = models.CharField()
    is_enabled = models.BooleanField()
    cur_data = models.CharField()

    class Meta:
        managed = False
        db_table = 'osd'


class PermReport(models.Model):
    pk = models.CompositePrimaryKey('app_id', 'report_id')
    app_id = models.TextField()
    report_name = models.TextField(blank=True, null=True)
    query = models.TextField(blank=True, null=True)
    report_config = models.TextField(blank=True, null=True)
    report_description = models.TextField(blank=True, null=True)
    report_id = models.DecimalField(max_digits=20, decimal_places=0)
    tag = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'perm_report'
        db_table_comment = "//report_config\r\n{\r\ncap:tion: 'Отчет 2323',\r\nparams: [\r\n  {name: 'Date1', type: 'datetime'},\r\n  {name: 'Date12, type: 'datetime'},\r\n],\r\nsql: 'select * from cp3.cp_subject_role'\r\n}"
        unique_together = (('app_id', 'report_id'),)


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    group_id = models.ForeignKey('PersonGroup', models.DO_NOTHING, db_column='group_id', to_field='group_id')
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'person'


class PersonGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    point_id = models.ForeignKey('Point', models.DO_NOTHING, db_column='point_id', to_field='point_id')
    class Meta:
        managed = False
        db_table = 'person_group'


class Point(models.Model):
    point_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    time_period = models.ForeignKey(FaceTimeSlot, models.DO_NOTHING, db_column='time_period')
    customer_id = models.IntegerField(blank=True, null=True)
    face_detection = models.ForeignKey(Method, models.DO_NOTHING)
    embedding = models.ForeignKey(Method, models.DO_NOTHING, related_name='point_embedding_set')
    demography = models.ForeignKey(Method, models.DO_NOTHING, related_name='point_demography_set')
    expiration_time = models.IntegerField(default=3)
    tag = models.TextField(null=True, blank=True, help_text='Класифікація магазинів на откуп клієнта')
    start_time = models.TimeField(default='09:30:00')
    end_time = models.TimeField(default='23:00:00')

    class Meta:
        managed = False
        db_table = 'point'
        db_table_comment = 'Елемент інфраструктури клієнта/корпорації\r\nto do\r\nприцепить клиент страна регион город'

class Param(models.Model):
    name = models.CharField(unique=True, max_length=255)
    group_name = models.TextField()
    datatype = models.CharField(max_length=50)
    view_order = models.IntegerField()
    eu = models.TextField(blank=True, null=True)
    display_label = models.TextField()
    display_type = models.TextField()
    enum_values = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    value = models.JSONField()
    enabled = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'param'

class HostContainerStatus(models.Model):
    host_name = models.TextField()
    container_name = models.TextField()
    status = models.TextField()
    collected_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'host_container_status'

class HostDiskUsage(models.Model):
    host_name = models.TextField()
    disk_path = models.TextField()
    total_size_gb = models.DecimalField(max_digits=10, decimal_places=2)
    used_space_gb = models.DecimalField(max_digits=10, decimal_places=2)
    collected_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'host_disk_usage'

class Metric(models.Model):
    metric_name = models.TextField()
    template = models.JSONField(db_comment='ключ - значение для значений параметров\r\n\r\nнапример\r\nобщий размер диска\r\nзанятый размер диска\r\nпроцент\r\nзанят картинками\r\nзанят ....\r\nзанят ....')
    comment = models.TextField(blank=True, null=True)
    metric_param = models.TextField(blank=True, null=True)
    cron = models.TextField(db_comment='строка cron (пока не реализвоано) to do пока работает 1раз в 5 минут (указано в cron менеджера)')
    enable = models.BooleanField()
    group_name = models.TextField(blank=True, null=True)
    sortord = models.SmallIntegerField(blank=True, null=True)
    metric_cmd = models.TextField()
    dashboard_view = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'metric'

class MetricHistory(models.Model):
    collected_at = models.DateTimeField()
    value = models.JSONField(blank=True, null=True)
    metric_id = models.ForeignKey(Metric, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'metric_history'

class LatestMetric(models.Model):
    id = models.IntegerField(primary_key=True)
    metric_name = models.CharField(max_length=255)
    template = models.JSONField()
    comment = models.TextField(null=True)
    metric_param = models.TextField()
    cron = models.CharField(max_length=100)
    enable = models.BooleanField()
    group_name = models.CharField(max_length=255)
    sortord = models.IntegerField()
    metric_cmd = models.TextField()
    dashboard_view = models.BooleanField()
    collected_at = models.DateTimeField()
    value = models.JSONField()

    class Meta:
        managed = False
        db_table = 'v_metric_last'

class ExportVCA(models.Model):
    point = models.CharField(max_length=255)
    date = models.DateTimeField()
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    customer_id = models.IntegerField()
    point_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'v_export_vca'

class VCustomerOrigin(models.Model):
    customer_id = models.IntegerField(null=True)
    origin = models.CharField(max_length=255)
    id = models.IntegerField(primary_key=True)
    point_id = models.IntegerField()
    origin_type_id = models.IntegerField()
    credentials = models.JSONField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    name = models.TextField(null=True, blank=True)
    success = models.BooleanField(blank=True, null=True)
    dt = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'v_customer_origin'

class VCustomerPerson(models.Model):
    customer_id = models.IntegerField(null=True)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    person_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField()
    name = models.CharField(max_length=255, null=True, blank=True)
    photo = models.BinaryField()

    class Meta:
        managed = False
        db_table = 'v_customer_person'

class VCustomerExport(models.Model):
    row_id = models.AutoField(primary_key=True)
    point_id = models.IntegerField()
    name = models.CharField(max_length=255, null=True, blank=True)  # point.name
    customer_id = models.IntegerField(null=True)
    ts = models.DateTimeField()  # truncated timestamp
    age = models.CharField(max_length=10, null=True, blank=True)  # extracted from JSON
    race = models.CharField(max_length=50, null=True, blank=True)
    emotion = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10)  # derived from dominant_gender

    class Meta:
        managed = False
        db_table = 'v_customer_export'

class UserCache(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, db_column='customer_id', to_field='customer_id', on_delete=models.DO_NOTHING)
    user_id = models.IntegerField()
    tenant_id = models.TextField()
    mode = models.TextField()

    class Meta:
        managed = False
        db_table = 'user_cache'
        unique_together = ('user_id', 'tenant_id', 'mode')

    def __str__(self):
        return f"UserCache(user_id={self.user_id}, tenant_id={self.tenant_id}, mode={self.mode})"

class Theme(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.ForeignKey(App, db_column='app_id', to_field='app_id', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    value = models.JSONField()
    sortord = models.IntegerField(null=True, blank=True)
    enabled = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'theme'

    def __str__(self):
        return f"{self.name} ({self.app_id})"

class ReportSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customer_id', to_field='customer_id')
    app_id = models.TextField()
    report_id = models.IntegerField()
    lang = models.TextField()
    cron = models.TextField(default='0 6 * * *')
    enable = models.BooleanField(default=False)
    last_dt = models.DateTimeField(auto_now=True)
    params = models.JSONField(null=True, blank=True, default=None)
    maillist = models.TextField()
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report_schedule'
        unique_together = ('customer', 'app_id', 'report_id', 'lang', 'params')

    def __str__(self):
        return f"Schedule: {self.customer_id} - {self.app_id} - {self.report_id} - {self.lang}"

class VReportSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customer_id', to_field='customer_id')
    app_id = models.TextField()
    report_id = models.IntegerField()
    lang = models.TextField()
    cron = models.TextField(default='0 6 * * *')
    enable = models.BooleanField(default=False)
    last_dt = models.DateTimeField(auto_now=True)
    params = models.JSONField(null=True, blank=True, default=None)
    maillist = models.TextField()
    report_name = models.TextField()
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'v_report_schedule'
        unique_together = ('customer', 'app_id', 'report_id', 'lang', 'params')

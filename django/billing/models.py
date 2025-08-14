from django.db import models
from django.contrib.postgres.fields import JSONField

class Balance(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    value = models.FloatField()
    crn = models.CharField(max_length=3)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'balance'
        managed = False

    def __str__(self):
        return f"Balance for Customer {self.customer_id}"

class TestOrder(models.Model):
    order_id = models.CharField(max_length=255, primary_key=True)
    amount = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'test_order'
        managed = False

    def __str__(self):
        return f"Order {self.order_id}"

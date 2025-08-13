from django.db import models

class Balance(models.Model):
    customer_id = models.IntegerField(primary_key=True)
#    value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    value = models.FloatField()
    crn = models.CharField(max_length=3)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'balance'
        managed = False

    def __str__(self):
        return f"Balance for Customer {self.customer_id}"

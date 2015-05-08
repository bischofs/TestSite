
from django.db import models
from audit_log.models.fields import LastUserField
from audit_log.models.managers import AuditLog
from simple_history.models import HistoricalRecords


class Ebench(models.Model):
    
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    parm1 = models.IntegerField()

    def __str__(self):
        return self.name

    histroy = HistoricalRecords()

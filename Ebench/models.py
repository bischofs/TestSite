
from django.db import models
from audit_log.models.fields import LastUserField
from audit_log.models.managers import AuditLog
from simple_history.models import HistoricalRecords


class Ebench(models.Model):
    
    Name = models.CharField(max_length=50)
    Model = models.CharField(max_length=50)
    CH4_Response_Factor = models.FloatField()
    CH4_Penetration_Factor = models.FloatField()
    Thermal_Chiller_Dewpoint = models.FloatField()
    Thermal_Absolute_Pressure = models.FloatField()
    THC_Initial_Contamination = models.FloatField()
    CH4_Initial_Contamination = models.FloatField()

    ##### Bottle Concentrations #####
    Bottle_Concentration_CO2 = models.FloatField()
    Bottle_Concentration_COH = models.FloatField()
    Bottle_Concentration_COL = models.FloatField()
    Bottle_Concentration_NOX = models.FloatField()
    Bottle_Concentration_THC = models.FloatField()
    Bottle_Concentration_NMHC = models.FloatField()

    def __str__(self):
        return self.Name

    history = HistoricalRecords()

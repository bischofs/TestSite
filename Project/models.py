from django.db import models
from Authentication.models import Account

class Project(models.Model):

    accounts  = models.ManyToManyField(Account) 
    name = models.CharField(max_length=30)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{0}'.format(self.name)




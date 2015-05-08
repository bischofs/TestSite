from django.contrib import admin
from Ebench.models import Ebench
from simple_history.admin import SimpleHistoryAdmin

class EbenchAdmin(SimpleHistoryAdmin):
    list_display = ('name',)


admin.site.register(Ebench, SimpleHistoryAdmin)
#simple_history.register(Ebench)

# Register your models here.

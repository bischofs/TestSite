# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebench', '0002_ebenchauditlogentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebenchauditlogentry',
            name='action_user',
        ),
        migrations.DeleteModel(
            name='EbenchAuditLogEntry',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DataTools', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='user',
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
    ]

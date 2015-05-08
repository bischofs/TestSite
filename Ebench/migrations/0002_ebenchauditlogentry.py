# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Ebench', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbenchAuditLogEntry',
            fields=[
                ('id', models.IntegerField(blank=True, verbose_name='ID', auto_created=True, db_index=True)),
                ('name', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('parm1', models.IntegerField()),
                ('action_id', models.AutoField(primary_key=True, serialize=False)),
                ('action_date', models.DateTimeField(editable=False, default=django.utils.timezone.now)),
                ('action_type', models.CharField(editable=False, max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')])),
                ('action_user', audit_log.models.fields.LastUserField(to=settings.AUTH_USER_MODEL, related_name='_ebench_audit_log_entry', editable=False, null=True)),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
    ]

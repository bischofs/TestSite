# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebench', '0004_historicalebench'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ebench',
            old_name='model',
            new_name='Model',
        ),
        migrations.RenameField(
            model_name='ebench',
            old_name='name',
            new_name='Name',
        ),
        migrations.RenameField(
            model_name='historicalebench',
            old_name='model',
            new_name='Model',
        ),
        migrations.RenameField(
            model_name='historicalebench',
            old_name='name',
            new_name='Name',
        ),
        migrations.RemoveField(
            model_name='ebench',
            name='parm1',
        ),
        migrations.RemoveField(
            model_name='historicalebench',
            name='parm1',
        ),
        migrations.AddField(
            model_name='ebench',
            name='CH4_Initial_Contamination',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='CH4_Penetration_Factor',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='CH4_Response_Factor',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='THC_Initial_Contamination',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Thermal_Absolute_Pressure',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Thermal_Chiller_Dewpoint',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='CH4_Initial_Contamination',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='CH4_Penetration_Factor',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='CH4_Response_Factor',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='THC_Initial_Contamination',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Thermal_Absolute_Pressure',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Thermal_Chiller_Dewpoint',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]

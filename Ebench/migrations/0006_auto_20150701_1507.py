# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebench', '0005_auto_20150512_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebench',
            name='Bottle_Concentration_CO2',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Bottle_Concentration_COH',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Bottle_Concentration_COL',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Bottle_Concentration_NMHC',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Bottle_Concentration_NOX',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebench',
            name='Bottle_Concentration_THC',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Bottle_Concentration_CO2',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Bottle_Concentration_COH',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Bottle_Concentration_COL',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Bottle_Concentration_NMHC',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Bottle_Concentration_NOX',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalebench',
            name='Bottle_Concentration_THC',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]

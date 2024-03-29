# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-08 15:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20170801_0851'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='termregistration',
            name='TermPayableFees',
        ),
        migrations.AddField(
            model_name='termpayablefees',
            name='Session',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Session', unique=True),
        ),
        migrations.AlterField(
            model_name='sponsorreceipt',
            name='Receipt_date',
            field=models.DateField(default=b'2017-08-08'),
        ),
        migrations.AlterField(
            model_name='termpayablefees',
            name='TermClassAdditionalFees',
            field=models.ManyToManyField(to='app.TermClassAdditionalFees'),
        ),
    ]

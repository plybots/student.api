# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-15 08:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balanceforwarded',
            name='Student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Student'),
        ),
        migrations.AlterField(
            model_name='sponsorreceipt',
            name='Receipt_date',
            field=models.DateField(default=b'2017-06-15'),
        ),
    ]

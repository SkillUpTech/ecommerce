# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-31 02:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher_code', '0002_auto_20190131_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vouchercode',
            name='expiration_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]

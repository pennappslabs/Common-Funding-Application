# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-25 14:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20170105_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cfauser',
            name='funder_name',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='cfauser',
            name='osa_email',
            field=models.EmailField(blank=True, help_text='The email address for contacting OSA when an app is funded.', max_length=254, null=True, verbose_name='OSA Contact Email'),
        ),
        migrations.AlterField(
            model_name='cfauser',
            name='user',
            field=models.OneToOneField(help_text='You must first create a user before adding them to the CFA.', on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cfauser',
            name='user_type',
            field=models.CharField(choices=[('R', 'REQUESTER'), ('F', 'FUNDER')], max_length=1),
        ),
        migrations.AlterField(
            model_name='eligibilityanswer',
            name='answer',
            field=models.CharField(choices=[('Y', 'YES'), ('N', 'NO')], max_length=1),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('S', 'SAVED'), ('B', 'SUBMITTED'), ('F', 'FUNDED'), ('W', 'FOLLOWUP'), ('O', 'OVER')], max_length=1),
        ),
        migrations.AlterField(
            model_name='funderconstraint',
            name='answer',
            field=models.CharField(choices=[('Y', 'YES'), ('N', 'NO')], max_length=1),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('H', 'Honoraria/Services'), ('E', 'Equipment/Supplies'), ('F', 'Food/Drinks'), ('S', 'Facilities/Security'), ('T', 'Travel/Conference'), ('P', 'Photocopies/Printing/Publicity'), ('O', 'Other')], max_length=1),
        ),
    ]

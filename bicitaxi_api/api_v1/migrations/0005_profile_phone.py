# Generated by Django 3.1.4 on 2021-03-14 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0004_locationassignation'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
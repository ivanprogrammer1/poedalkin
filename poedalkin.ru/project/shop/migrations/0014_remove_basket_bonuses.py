# Generated by Django 4.1 on 2022-12-03 20:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_order_status_order_work_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='bonuses',
        ),
    ]

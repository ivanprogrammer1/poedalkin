# Generated by Django 4.1 on 2022-11-18 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_order_bonuses_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basketitem',
            name='count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
# Generated by Django 4.1 on 2022-11-18 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_basket_bonuses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='apartment',
        ),
        migrations.RemoveField(
            model_name='order',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='order',
            name='door_code',
        ),
        migrations.RemoveField(
            model_name='order',
            name='entrance',
        ),
        migrations.RemoveField(
            model_name='order',
            name='floor',
        ),
        migrations.RemoveField(
            model_name='order',
            name='house',
        ),
        migrations.RemoveField(
            model_name='order',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='order',
            name='street',
        ),
        migrations.RemoveField(
            model_name='orderaddressuser',
            name='address',
        ),
    ]

# Generated by Django 4.1 on 2022-11-18 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_orderitem_count_alter_orderitem_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='bonuses',
            field=models.PositiveBigIntegerField(default=0, verbose_name='Бонусы'),
        ),
    ]
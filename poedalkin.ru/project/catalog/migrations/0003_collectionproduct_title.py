# Generated by Django 4.1 on 2022-10-01 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_collectionproduct_remove_product_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionproduct',
            name='title',
            field=models.CharField(max_length=200, null=True, verbose_name='Имя'),
        ),
    ]

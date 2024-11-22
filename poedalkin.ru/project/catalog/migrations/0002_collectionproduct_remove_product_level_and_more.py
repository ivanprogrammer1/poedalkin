# Generated by Django 4.1 on 2022-10-01 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='level',
        ),
        migrations.RemoveField(
            model_name='product',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='product',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='product',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tree_id',
        ),
        migrations.AddField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='catalog.collectionproduct', verbose_name='Коллекция'),
        ),
    ]

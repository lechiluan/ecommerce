# Generated by Django 4.1.7 on 2023-04-11 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_orders_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='view_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
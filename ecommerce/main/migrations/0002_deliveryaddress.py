# Generated by Django 4.1.7 on 2023-03-14 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=40, null=True)),
                ('last_name', models.CharField(max_length=40, null=True)),
                ('mobile', models.CharField(max_length=20, null=True)),
                ('email', models.CharField(max_length=50, null=True)),
                ('address', models.CharField(max_length=500, null=True)),
                ('city', models.CharField(max_length=40, null=True)),
                ('state', models.CharField(max_length=40, null=True)),
                ('zip_code', models.CharField(max_length=20, null=True)),
                ('date_added', models.DateField(auto_now_add=True, null=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.customer')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.orders')),
            ],
        ),
    ]
# Generated by Django 4.1.7 on 2023-03-31 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_brand_description_brand_slug_category_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
    ]
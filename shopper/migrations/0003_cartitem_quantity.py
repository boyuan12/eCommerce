# Generated by Django 3.1.3 on 2020-12-03 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopper', '0002_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
# Generated by Django 3.1.3 on 2022-12-23 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopper', '0010_cartitem_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='is_payout',
            field=models.BooleanField(default=False),
        ),
    ]
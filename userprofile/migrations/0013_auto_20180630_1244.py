# Generated by Django 2.0.4 on 2018-06-30 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0012_userpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpayment',
            name='method_payment',
            field=models.CharField(choices=[('MN', 'MANUAL PAYMENT'), ('VA', 'VIRTUAL ACCOUNT'), ('TR', 'TRANSFER')], default='MN', max_length=2),
        ),
    ]

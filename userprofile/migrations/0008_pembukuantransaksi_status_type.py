# Generated by Django 2.0.4 on 2018-05-16 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0007_profile_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='pembukuantransaksi',
            name='status_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Topup saldo'), (2, 'Reversed'), (9, 'Success'), (3, 'Failed')], default=9),
        ),
    ]

# Generated by Django 2.0.4 on 2018-06-04 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0008_catatanmodal_biller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catatanmodal',
            name='biller',
            field=models.CharField(choices=[('SB', 'Siap Bayar'), ('RB', 'Raja Biller')], default='SB', max_length=2),
        ),
    ]

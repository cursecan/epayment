# Generated by Django 2.0.4 on 2018-06-18 03:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mpulsa', '0007_auto_20180607_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaksi',
            name='pembukuan',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userprofile.PembukuanTransaksi'),
        ),
    ]

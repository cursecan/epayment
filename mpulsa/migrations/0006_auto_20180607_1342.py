# Generated by Django 2.0.4 on 2018-06-07 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpulsa', '0005_auto_20180604_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='kode_produk',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='no_hp',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='ref1',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='ref2',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='sn',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='status',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='waktu',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
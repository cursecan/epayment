# Generated by Django 2.0.4 on 2018-07-04 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egame', '0002_auto_20180704_1108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='panduan_transaksi',
        ),
        migrations.AddField(
            model_name='game',
            name='help_text',
            field=models.TextField(blank=True, max_length=2000),
        ),
        migrations.DeleteModel(
            name='CaraTransaksi',
        ),
    ]

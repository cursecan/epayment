# Generated by Django 2.0.4 on 2018-07-04 04:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('egame', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaraTransaksi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_game', models.CharField(max_length=50)),
                ('cara_transaksi', models.TextField(max_length=2000)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='panduan_transaksi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='egame.CaraTransaksi'),
        ),
    ]

# Generated by Django 2.0.4 on 2018-05-27 05:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userprofile', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kode', models.CharField(max_length=10, unique=True)),
                ('operator', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kode_internal', models.CharField(blank=True, max_length=10)),
                ('nominal', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('kode_external', models.CharField(max_length=15)),
                ('price_beli', models.PositiveIntegerField(default=0)),
                ('keterangan', models.CharField(blank=True, max_length=200)),
                ('parse_text', models.CharField(blank=True, max_length=200)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=False)),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='etransport.Operator')),
            ],
            options={
                'ordering': ['operator', 'nominal'],
            },
        ),
        migrations.CreateModel(
            name='ResponseTransaksi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_code', models.CharField(blank=True, max_length=200)),
                ('info', models.CharField(blank=True, max_length=200)),
                ('product_code', models.CharField(blank=True, max_length=20)),
                ('trxtime', models.CharField(blank=True, max_length=50)),
                ('nohp', models.CharField(blank=True, max_length=30)),
                ('serial_no', models.CharField(blank=True, max_length=100)),
                ('price', models.PositiveIntegerField(default=0)),
                ('balance', models.PositiveIntegerField(default=0)),
                ('refca', models.CharField(blank=True, max_length=50)),
                ('refsb', models.CharField(blank=True, max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaksi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trx_code', models.CharField(blank=True, max_length=16)),
                ('price', models.PositiveIntegerField(default=0)),
                ('phone', models.CharField(max_length=20)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Success'), (1, 'Pending'), (9, 'Gagal')], default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('pembukuan', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bukutrans', to='userprofile.PembukuanTransaksi')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='etransport.Product')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='usertrans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='responsetransaksi',
            name='trx',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='etransport.Transaksi'),
        ),
    ]
# Generated by Django 2.0.4 on 2018-07-02 05:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0014_auto_20180701_1644'),
        ('etransport', '0004_auto_20180702_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResponseTransaksiRb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('waktu', models.CharField(blank=True, max_length=40)),
                ('no_hp', models.CharField(blank=True, max_length=20)),
                ('sn', models.CharField(blank=True, max_length=100)),
                ('ref1', models.CharField(blank=True, max_length=30)),
                ('ref2', models.CharField(blank=True, max_length=30)),
                ('status', models.CharField(blank=True, max_length=20)),
                ('ket', models.CharField(blank=True, max_length=100)),
                ('saldo_terpotong', models.PositiveIntegerField(default=0)),
                ('sisa_saldo', models.PositiveIntegerField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('trx', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='etransport.Transaksi')),
            ],
        ),
        migrations.CreateModel(
            name='TransaksiRb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trx_code', models.CharField(blank=True, max_length=16)),
                ('price', models.PositiveIntegerField(default=0)),
                ('phone', models.CharField(max_length=20)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Success'), (1, 'Pending'), (9, 'Gagal')], default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('catatan_modal', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='etrans_rbcctt_modal', to='userprofile.CatatanModal')),
                ('pembukuan', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='etrans_rbbuku_transaksi', to='userprofile.PembukuanTransaksi')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='etransport.Product')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='etrans_rbuser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['-timestamp'],
            },
        ),
    ]

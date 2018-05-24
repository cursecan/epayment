# Generated by Django 2.0.4 on 2018-05-24 05:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PembukuanTransaksi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seq', models.PositiveSmallIntegerField(default=1)),
                ('debit', models.IntegerField(default=0)),
                ('kredit', models.IntegerField(default=0)),
                ('balance', models.IntegerField(default=0)),
                ('status_type', models.PositiveSmallIntegerField(choices=[(1, 'Topup saldo'), (2, 'Reversed'), (9, 'Success'), (3, 'Failed')], default=9)),
                ('keterangan', models.CharField(blank=True, max_length=200)),
                ('confrmed', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('parent_id', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userprofile.PembukuanTransaksi')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=25)),
                ('telegram', models.CharField(blank=True, max_length=25)),
                ('saldo', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=False)),
                ('agen', models.BooleanField(default=False)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('token_code', models.CharField(blank=True, max_length=10)),
                ('limit', models.IntegerField(default=-50000)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

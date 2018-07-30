# Generated by Django 2.0.4 on 2018-07-29 11:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0015_soldmarking'),
    ]

    operations = [
        migrations.CreateModel(
            name='PembukuanPartner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nominal', models.PositiveIntegerField()),
                ('flag', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partner', to=settings.AUTH_USER_MODEL)),
                ('user_lfg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flg', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='saldo_agen',
            field=models.IntegerField(default=0),
        ),
    ]
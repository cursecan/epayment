# Generated by Django 2.0.4 on 2018-07-02 07:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('etransport', '0005_responsetransaksirb_transaksirb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsetransaksirb',
            name='trx',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='etransport.TransaksiRb'),
        ),
    ]
# Generated by Django 2.0.4 on 2018-05-27 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_catatanmodal'),
    ]

    operations = [
        migrations.AddField(
            model_name='catatanmodal',
            name='parent_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userprofile.CatatanModal'),
        ),
    ]

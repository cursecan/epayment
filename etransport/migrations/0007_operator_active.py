# Generated by Django 2.0.4 on 2018-07-02 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etransport', '0006_auto_20180702_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
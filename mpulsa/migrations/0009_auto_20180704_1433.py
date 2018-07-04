# Generated by Django 2.0.4 on 2018-07-04 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpulsa', '0008_auto_20180618_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='operator',
            name='help_text',
            field=models.TextField(blank=True, max_length=2000),
        ),
    ]

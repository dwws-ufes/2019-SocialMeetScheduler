# Generated by Django 2.2.8 on 2019-12-11 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meet', '0008_auto_20191021_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='marker',
            name='ld_point',
            field=models.URLField(blank=True, default=None, null=True),
        ),
    ]

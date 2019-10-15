# Generated by Django 2.2.6 on 2019-10-15 07:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('meet', '0005_auto_20191015_0744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marker',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]

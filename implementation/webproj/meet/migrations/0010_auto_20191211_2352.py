# Generated by Django 2.2.8 on 2019-12-11 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meet', '0009_marker_ld_point'),
    ]

    operations = [
        migrations.RenameField(
            model_name='marker',
            old_name='ld_point',
            new_name='point_ld',
        ),
    ]
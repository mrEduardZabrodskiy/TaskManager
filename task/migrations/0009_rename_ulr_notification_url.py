# Generated by Django 4.2.3 on 2024-04-17 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0008_rename_email_confrim_status_userprofile_email_confirm_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='ulr',
            new_name='url',
        ),
    ]

# Generated by Django 5.1.6 on 2025-05-31 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_customuser_firebase_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user_permissions',
        ),
        migrations.DeleteModel(
            name='ChatMessage',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]

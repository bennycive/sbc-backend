# Generated by Django 4.2.20 on 2025-06-14 05:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('colleges_api', '0001_initial'),
        ('users_api', '0009_merge_20250614_0634'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='colleges_api.course'),
        ),
        migrations.AlterField(
            model_name='studentcertificate',
            name='certificate_file',
            field=models.FileField(upload_to='student_certificates'),
        ),
    ]

# Generated by Django 4.2.20 on 2025-05-15 20:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranscriptCertificateRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('both', 'Certificate and Transcript'), ('certificate', 'Certificate Only'), ('transcript', 'Transcript Only')], max_length=20)),
                ('number_of_copies', models.PositiveIntegerField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('bursar_verified', models.BooleanField(default=False)),
                ('hod_verified', models.BooleanField(default=False)),
                ('exam_officer_approved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProvisionalResultRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_address', models.CharField(max_length=255)),
                ('email_or_phone', models.CharField(max_length=100)),
                ('year_of_admission', models.CharField(max_length=20)),
                ('year_of_study', models.CharField(max_length=20)),
                ('programme', models.CharField(max_length=255)),
                ('semester_range', models.CharField(choices=[('one', 'Semester I'), ('two', 'Semester II')], max_length=30)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('bursar_verified', models.BooleanField(default=False)),
                ('hod_verified', models.BooleanField(default=False)),
                ('exam_officer_approved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

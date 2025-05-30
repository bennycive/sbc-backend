# Generated by Django 4.2.20 on 2025-05-15 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('colleges_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('role', models.CharField(choices=[('student', 'Student'), ('hod', 'Head of Department'), ('teacher', 'Teacher'), ('bursar', 'Bursar'), ('exam-officer', 'Exam-officer'), ('principal', 'Principal'), ('admin', 'admin')], max_length=20)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yos', models.PositiveIntegerField(blank=True, null=True, verbose_name='Year of Study')),
                ('nida', models.CharField(max_length=255, unique=True)),
                ('phone_number', models.CharField(max_length=30)),
                ('image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='colleges_api.department')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('type', models.CharField(choices=[('Receipt', 'Receipt'), ('Bill', 'Bill')], max_length=20)),
                ('payment_type', models.CharField(choices=[('Tuition Fees-Undergraduate', 'Tuition Fees-Undergraduate')], max_length=100)),
                ('remark', models.CharField(choices=[('Private', 'Private'), ('HESLB', 'HESLB')], max_length=100)),
                ('reference_no', models.CharField(max_length=100)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('payment', models.DecimalField(decimal_places=2, max_digits=12)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users_api.academicyear')),
                ('student', models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='OtherPaymentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('type', models.CharField(choices=[('Receipt', 'Receipt'), ('Bill', 'Bill')], max_length=20)),
                ('payment_type', models.CharField(choices=[('Accommodation Fees', 'Accommodation Fees'), ('Quality Assurance Collection', 'Quality Assurance Collection'), ('Health Services Income', 'Health Services Income'), ('Contribution to UDOM', 'Contribution to UDOM'), ('Other', 'Other')], max_length=100)),
                ('remark', models.CharField(choices=[('Private', 'Private'), ('Standard Bills', 'Standard Bills')], max_length=100)),
                ('reference_no', models.CharField(max_length=100, null=True)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payment', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users_api.academicyear')),
                ('student', models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]

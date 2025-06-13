from django.db import models
from django.contrib.auth.models import User
from colleges_api.models import Department
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # Prompt for role if not provided
        role = extra_fields.get('role')
        if not role:
            from django.core.management import call_command
            import getpass
            role = input("Enter User role (E.g , admin, principal, teacher,bursar,exam-officer, student, hod): ")
            extra_fields['role'] = role

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    ROLE_CHOICES = [
        
        ('student', 'Student'),
        ('hod', 'Head of Department'),
        ('teacher', 'Teacher'),
        ('bursar','Bursar'),
        ('exam-officer','Exam-officer'),
        ('principal', 'Principal'),
        ('admin', 'admin'),
        
    ]
    

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=False, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=30, default=0)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(null=False , max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

class AcademicYear(models.Model):
    year = models.CharField(max_length=20, unique=True)  # e.g., "2022/2023"

    def __str__(self):
        return self.year


class Profile(models.Model):
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    yos = models.PositiveIntegerField(verbose_name='Year of Study', null=True, blank=True)
    nida = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=30)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    webauthn_credential_id = models.TextField(null=True, blank=True)
    webauthn_public_key = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"
    
    
class PaymentRecord(models.Model):
    
    PAYMENT_TYPE_CHOICES = [
    ('Tuition Fees-Undergraduate', 'Tuition Fees-Undergraduate'),
   ]
    
    PAYMENT_REMARKS = [
         ('Private','Private'),
         ('HESLB','HESLB'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=[('Receipt', 'Receipt'), ('Bill', 'Bill')])
    payment_type = models.CharField(
        max_length=100,
        choices=PAYMENT_TYPE_CHOICES
    )
    remark = models.CharField(max_length=100, choices=PAYMENT_REMARKS)
    reference_no = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    payment = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.student.username} - {self.payment_type} - {self.date}"


class OtherPaymentRecord(models.Model):
    
    PAYMENT_TYPE_CHOICES = [
        
        ('Accommodation Fees', 'Accommodation Fees'),
        ('Quality Assurance Collection', 'Quality Assurance Collection'),
        ('Health Services Income', 'Health Services Income'),
        ('Contribution to UDOM', 'Contribution to UDOM'),
        ('Other', 'Other'),
    ]
    
    PAYMENT_REMARKS = [
         ('Private','Private'),
         ('Standard Bills','Standard Bills'),
    ] 
        
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=[('Receipt', 'Receipt'), ('Bill', 'Bill')])
    payment_type = models.CharField(max_length=100, choices=PAYMENT_TYPE_CHOICES )
    remark = models.CharField(max_length=100, choices=PAYMENT_REMARKS)
    reference_no = models.CharField(max_length=100, null=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    payment = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.student.username} - {self.payment_type} - {self.date}"



class TranscriptCertificateRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('both', 'Certificate and Transcript'),
        ('certificate', 'Certificate Only'),
        ('transcript', 'Transcript Only'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    number_of_copies = models.PositiveIntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    bursar_verified = models.BooleanField(default=False)
    hod_verified = models.BooleanField(default=False)
    exam_officer_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.get_request_type_display()}"
    
    
    
class ProvisionalResultRequest(models.Model):
    SEMESTER_RANGE_CHOICES = [
        ('one', 'Semester I'),
        ('two', 'Semester II'),
        ('all', 'First Year to Second Year'),  
        
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    current_address = models.CharField(max_length=255)
    email_or_phone = models.CharField(max_length=100)
    year_of_admission = models.CharField(max_length=20)
    year_of_study = models.CharField(max_length=20)
    programme = models.CharField(max_length=255)
    semester_range = models.CharField(max_length=30, choices=SEMESTER_RANGE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)

    bursar_verified = models.BooleanField(default=False)
    hod_verified = models.BooleanField(default=False)
    exam_officer_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Provisional Request by {self.user}"



class StudentCertificate(models.Model):
    CERTIFICATE_TYPES = [
        ('birth_certificate', 'Birth Certificate'),
        ('form_4_certificate', 'Form 4 Certificate'),
        ('form_6_certificate', 'Form 6 Certificate'),
        ('diploma_certificate', 'Diploma Certificate'),
        ('voter_id', 'Voter ID'),
        ('nin_id', 'NIN ID'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=50, choices=CERTIFICATE_TYPES)
    certificate_name = models.CharField(max_length=255)  # e.g., actual document name or description
    certificate_file = models.FileField(upload_to='student_certificates/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.get_certificate_type_display()} - {self.certificate_name}"


class Fingerprint(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fingerprint_data = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

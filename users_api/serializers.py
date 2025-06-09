from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# from rest_framework.validators import UniqueValidator # Not explicitly used in your provided code, can be removed if not needed elsewhere
from .models import (
    CustomUser, Profile, AcademicYear, PaymentRecord, OtherPaymentRecord,
    TranscriptCertificateRequest, ProvisionalResultRequest, StudentCertificate
)
# Assuming Department model is in colleges_api.models and imported correctly where ProfileSerializer might use it
# If Department is in the current app, use from .models import Department
# For now, assuming the import from colleges_api.models import Department is for Profile's FK if it were nested.
# Since ProfileSerializer just lists 'department' (which will be an ID), the direct import isn't strictly needed
# at the top level here unless DepartmentSerializer is also defined and used.

# --- Token Serializer (Usually for Authentication) ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token
        token['username'] = user.username
        token['email'] = user.email
        token['id'] = user.id
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user details to the response when a token is obtained
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name, # Added
            'last_name': self.user.last_name,   # Added
            'role': self.user.role,
            'department': self.user.department, # Added
        }
        return data

# --- User and Profile Serializers ---
class CustomUserSerializer(serializers.ModelSerializer):
    # Make password write-only and not strictly required for read/update operations
    # where password isn't being changed.
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        # Explicitly list fields for clarity and control, especially when nesting
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'role', 'department', 'is_active',
            'is_staff', 'is_superuser', 'date_joined', 'password' # Password included for write operations
        ]
        read_only_fields = ['date_joined'] # Fields not typically set on create/update

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(**validated_data) # Use manager for creation
        # The create_user manager method already handles set_password if password is provided
        # If you pass password to create_user, it will be handled.
        # If password was popped and you want to ensure it's set if present:
        # if password:
        #     user.set_password(password)
        #     user.save() # create_user already saves
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password: # If a new password was provided
            instance.set_password(password)
        instance.save()
        return instance

class ProfileSerializer(serializers.ModelSerializer):
    # If you want to show department NAME instead of ID here:
    # department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    # Then include 'department_name' in fields instead of or in addition to 'department'
    class Meta:
        model = Profile
        fields = ['id', 'user', 'yos', 'nida', 'phone_number', 'department', 'image']
        # If 'user' should be nested here too:
        # user = CustomUserSerializer(read_only=True) # Or specify a simpler user serializer

# --- Academic and Payment Serializers (Assuming these are okay as is for now) ---
class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class PaymentRecordSerializer(serializers.ModelSerializer):
    # To show student name instead of ID:
    # student_name = serializers.CharField(source='student.get_full_name', read_only=True) # or student.username
    class Meta:
        model = PaymentRecord
        fields = '__all__' # Consider listing fields and adding student_name if needed

class OtherPaymentRecordSerializer(serializers.ModelSerializer):
    # Similar to PaymentRecordSerializer, consider student_name if needed
    class Meta:
        model = OtherPaymentRecord
        fields = '__all__'

# --- Request Serializers (Key Updates Here) ---
class TranscriptCertificateRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)  # NESTED USER DETAILS
    # Provides the program name. Assumes 'CustomUser.department' stores the program string.
    # Adjust 'source' if program info is elsewhere (e.g., user.profile.department.name).
    program = serializers.CharField(source='user.department', read_only=True, allow_null=True)

    class Meta:
        model = TranscriptCertificateRequest
        fields = [
            'id', 'user', 'request_type', 'number_of_copies', 'submitted_at',
            'bursar_verified', 'hod_verified', 'exam_officer_approved',
            'program'  # Include the program field in the output
        ]

class ProvisionalResultRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)  # NESTED USER DETAILS
    # The 'programme' field is already part of the ProvisionalResultRequest model.
    # Using 'fields = __all__' or explicitly listing it will include it.

    class Meta:
        model = ProvisionalResultRequest
        fields = [ # Explicitly listing for clarity
            'id', 'user', 'current_address', 'email_or_phone', 'year_of_admission',
            'year_of_study', 'programme', 'semester_range', 'submitted_at',
            'bursar_verified', 'hod_verified', 'exam_officer_approved'
        ]

# --- Certificate Serializer ---
class StudentCertificateSerializer(serializers.ModelSerializer):
    # To send 'certificate_name' as 'name' to match a common Angular interface pattern.
    # If your Angular interface uses 'certificate_name', you don't need this alias.
    name = serializers.CharField(source='certificate_name', read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    # To show student username or ID (currently 'student' field will be the ID)
    # student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = StudentCertificate
        fields = [
            'id',
            'student', # This will be the student's ID by default
            # 'student_username', # If you add the line above
            'certificate_type',
            'certificate_name', # Original model field name
            'name',             # Aliased field for 'certificate_name'
            # 'certificate_file', # The raw FileField, file_url is usually preferred for frontend
            'file_url',
            'uploaded_at',
            # Add 'user' which seems to be expected by Angular Certificate interface, map from 'student.id'
            # However, the Angular interface has 'user: number'. 'student' (PK) already fulfills this.
            # If Angular's 'user' field in Certificate interface specifically means the user's ID,
            # then 'student' being a PK in the response is fine.
        ]
        read_only_fields = ['id', 'uploaded_at', 'file_url', 'name']

    def get_file_url(self, obj):
        request = self.context.get('request')
        # Ensure certificate_file has a value and a url attribute
        if obj.certificate_file and hasattr(obj.certificate_file, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.certificate_file.url)
            return obj.certificate_file.url # Fallback if request context not available (less ideal)
        return None

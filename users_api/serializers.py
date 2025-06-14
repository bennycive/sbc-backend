from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import (
    CustomUser, Profile, AcademicYear, PaymentRecord, OtherPaymentRecord,
    TranscriptCertificateRequest, ProvisionalResultRequest, StudentCertificate, Fingerprint
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['id'] = user.id
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'department': self.user.department,
        }
        return data

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'role', 'department', 'is_active',
            'is_staff', 'is_superuser', 'date_joined', 'password'
        ]
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

from colleges_api.models import Department

class ProfileSerializer(serializers.ModelSerializer):
    yos = serializers.IntegerField(required=False, allow_null=True)
    nida = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'yos', 'nida', 'phone_number', 'department', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # queryset is set directly on department field, no dynamic setting needed

    # No get_fields override needed

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = '__all__'

class OtherPaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherPaymentRecord
        fields = '__all__'

class TranscriptCertificateRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    program = serializers.CharField(source='user.department', read_only=True, allow_null=True)

    class Meta:
        model = TranscriptCertificateRequest
        fields = [
            'id', 'user', 'request_type', 'number_of_copies', 'submitted_at',
            'bursar_verified', 'hod_verified', 'exam_officer_approved',
            'program'
        ]

class ProvisionalResultRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = ProvisionalResultRequest
        fields = [
            'id', 'user', 'current_address', 'email_or_phone', 'year_of_admission',
            'year_of_study', 'programme', 'semester_range', 'submitted_at',
            'bursar_verified', 'hod_verified', 'exam_officer_approved'
        ]

class StudentCertificateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='certificate_name', read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentCertificate
        fields = [
            'id',
            'student',
            'certificate_type',
            'certificate_name',
            'name',
            'file_url',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at', 'file_url', 'name']
        extra_kwargs = {'certificate_file': {'required': True}}

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.certificate_file and hasattr(obj.certificate_file, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.certificate_file.url)
            return obj.certificate_file.url
        return None

# class FingerprintSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Fingerprint
#         fields = ['id', 'student', 'fingerprint_data', 'uploaded_at']
#         read_only_fields = ['id', 'uploaded_at']


class FingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fingerprint
        fields = ['id', 'student', 'fingerprint_data', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def create(self, validated_data):
        print("Received validated data:", validated_data)
        return super().create(validated_data)

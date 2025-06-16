from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import WebAuthnDevice 

from .models import (
    CustomUser, Profile, AcademicYear, PaymentRecord, OtherPaymentRecord,
    TranscriptCertificateRequest, ProvisionalResultRequest, StudentCertificate
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
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

from colleges_api.models import Department, Course

class ProfileSerializer(serializers.ModelSerializer):
    yos = serializers.IntegerField(required=False, allow_null=True)
    nida = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False, allow_null=True)
    program = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'yos', 'nida', 'phone_number', 'department', 'program', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # queryset is set directly on department and program fields, no dynamic setting needed

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
        
# PAYMENT SERIALIZER FOR THE BURSAR 
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
    payment_records = serializers.SerializerMethodField()
    other_payment_records = serializers.SerializerMethodField()

    class Meta:
        model = TranscriptCertificateRequest
        fields = [
            'id', 'user', 'request_type', 'number_of_copies', 'submitted_at',
            'bursar_verified', 'hod_verified', 'exam_officer_approved',
            'program', 'payment_records', 'other_payment_records'
        ]

    def get_payment_records(self, obj):
        if obj.user is None:
            return []
        payments = obj.user.paymentrecord_set.all()
        return PaymentRecordSerializer(payments, many=True).data

    def get_other_payment_records(self, obj):
        if obj.user is None:
            return []
        other_payments = obj.user.otherpaymentrecord_set.all()
        return OtherPaymentRecordSerializer(other_payments, many=True).data

class ProvisionalResultRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    payment_records = serializers.SerializerMethodField()
    other_payment_records = serializers.SerializerMethodField()

    class Meta:
        model = ProvisionalResultRequest
        fields = [
            'id', 'user', 'current_address', 'email_or_phone', 'year_of_admission',
            'year_of_study', 'programme', 'semester_range', 'submitted_at',
            'bursar_verified', 'hod_verified', 'exam_officer_approved',
            'payment_records', 'other_payment_records'
        ]

    def get_payment_records(self, obj):
        payments = obj.user.paymentrecord_set.all()
        return PaymentRecordSerializer(payments, many=True).data

    def get_other_payment_records(self, obj):
        other_payments = obj.user.otherpaymentrecord_set.all()
        return OtherPaymentRecordSerializer(other_payments, many=True).data

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

# class StudentCertificateSerializer(serializers.ModelSerializer):
#     """
#     Serializes StudentCertificate objects.
#     - Allows an admin to assign a certificate to a student via their ID.
#     - Generates a full, absolute URL for the certificate file.
#     """
#     # This field accepts a student's ID during POST/PUT requests from an admin.
#     # It validates that the ID belongs to a user with the 'student' role.
#     student = serializers.PrimaryKeyRelatedField(
#         queryset=CustomUser.objects.filter(role='student')
#     )

#     # This read-only field will contain the full URL for the frontend.
#     file_url = serializers.SerializerMethodField()

#     # This field is for the actual file upload and is not included in the response.
#     certificate_file = serializers.FileField(write_only=True, required=True)

#     class Meta:
#         model = StudentCertificate
#         fields = [
#             'id',
#             'student',
#             'certificate_type',
#             'certificate_name',
#             'certificate_file', # For upload (write-only)
#             'file_url',         # For response (read-only)
#             'uploaded_at',
#         ]
#         read_only_fields = ['id', 'uploaded_at', 'file_url']

#     def get_file_url(self, obj):
#         """
#         This method builds the absolute URL for the certificate file.
#         It relies on the 'request' being passed into the serializer's context.
#         """
#         request = self.context.get('request')
#         # Check if the file exists and a request object is available
#         if obj.certificate_file and request:
#             return request.build_absolute_uri(obj.certificate_file.url)
#         return None

#     def to_representation(self, instance):
#         """
#         Customizes the JSON output for GET requests to show full student details,
#         which is more useful for the UI than just an ID.
#         """
#         representation = super().to_representation(instance)
#         student_instance = instance.student
#         representation['student'] = {
#             'id': student_instance.id,
#             'username': student_instance.username,
#             'first_name': student_instance.first_name,
#             'last_name': student_instance.last_name,
#         }
#         return representation


class WebAuthnDeviceSerializer(serializers.ModelSerializer):
    # For BinaryField types (credential_id, public_key),
    # it's best to represent them as base64url strings in JSON
    # so they can be easily consumed by the frontend.
    # The pywebauthn library handles the byte conversion on the backend.
    credential_id = serializers.CharField()
    public_key = serializers.CharField()
    aaguid = serializers.CharField(required=False, allow_null=True) # UUIDField can be represented as string

    class Meta:
        model = WebAuthnDevice
        fields = [
            'id',
            'user', # Or 'student' if your CustomUser is actually 'Student'
            'name',
            'credential_id',
            'public_key',
            'attestation_format',
            'aaguid',
            'sign_count',
            'credential_type',
            'registered_at',
        ]
        read_only_fields = [
            'id',
            'user', # Typically, the user is set by the view, not sent by client for creation
            'registered_at',
            'sign_count', # This is updated by the server during authentication
        ]

    def create(self, validated_data):
        # When creating, ensure binary fields are converted from base64url strings
        # that might be sent by the client, if you allow creation via this serializer.
        # However, for WebAuthn registration, the verification view typically
        # handles the creation directly after `verify_registration_response`.
        if 'credential_id' in validated_data:
            validated_data['credential_id'] = self.base64url_to_bytes(validated_data['credential_id'])
        if 'public_key' in validated_data:
            validated_data['public_key'] = self.base64url_to_bytes(validated_data['public_key'])
        
        # If 'user' isn't explicitly provided, ensure it's set from context or request.
        # This serializer would primarily be for listing/retrieving devices.
        # For actual registration, the view's `WebAuthnDevice.objects.create` is preferred.
        return super().create(validated_data)

    def to_representation(self, instance):
        # Convert binary fields to base64url strings for JSON output
        ret = super().to_representation(instance)
        if instance.credential_id:
            ret['credential_id'] = self.bytes_to_base64url(instance.credential_id)
        if instance.public_key:
            ret['public_key'] = self.bytes_to_base64url(instance.public_key)
        return ret
    
    # Helper methods (can be shared or placed in utils if used widely)
    def base64url_to_bytes(self, data):
        import base64
        padding = '=' * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ''
        return base64.urlsafe_b64decode(data + padding)

    def bytes_to_base64url(self, data):
        import base64
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
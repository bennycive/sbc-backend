from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, Profile,AcademicYear, PaymentRecord, OtherPaymentRecord
from colleges_api.models import Department
from .models import TranscriptCertificateRequest, ProvisionalResultRequest


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
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }
        
        return data



# USER SERIALIZER
class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = CustomUser
        fields = '__all__'  

    def create(self, validated_data):
        password = validated_data.pop('password') 
        user = CustomUser(**validated_data)
        user.set_password(password)  
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

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id','user', 'yos', 'nida', 'phone_number', 'department', 'program', 'image']


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
    class Meta:
        model = TranscriptCertificateRequest
        fields = '__all__'

class ProvisionalResultRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionalResultRequest
        fields = '__all__'
        
        

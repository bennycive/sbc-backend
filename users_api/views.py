from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, AcademicYear, PaymentRecord, OtherPaymentRecord
from .serializers import CustomUserSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
import json
from django.http import JsonResponse
from rest_framework import viewsets
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer, AcademicYearSerializer, PaymentRecordSerializer, OtherPaymentRecordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from .models import TranscriptCertificateRequest, ProvisionalResultRequest
from .serializers import TranscriptCertificateRequestSerializer, ProvisionalResultRequestSerializer
from .models import StudentCertificate
from rest_framework.permissions import AllowAny

from rest_framework.permissions import IsAdminUser
from colleges_api.models import Department, Course
from django.db import models

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]


class PaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]


class OtherPaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = OtherPaymentRecord.objects.all()
    serializer_class = OtherPaymentRecordSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class TranscriptCertificateRequestViewSet(viewsets.ModelViewSet):
    queryset = TranscriptCertificateRequest.objects.all().order_by('-submitted_at')
    serializer_class = TranscriptCertificateRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.profile.fingerprint_verified:
            raise PermissionDenied("Fingerprint verification required before requesting certificates or transcripts.")
        serializer.save(user=user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'student':
            return TranscriptCertificateRequest.objects.filter(user=user).order_by('-submitted_at')
        return TranscriptCertificateRequest.objects.none()

class ProvisionalResultRequestViewSet(viewsets.ModelViewSet):
    queryset = ProvisionalResultRequest.objects.all().order_by('-submitted_at')
    serializer_class = ProvisionalResultRequestSerializer
    permission_classes = [AllowAny] # Currently allowing any access
    # permission_classes = [permissions.IsAuthenticated] # Commented out


from .serializers import StudentCertificateSerializer

class StudentCertificateViewSet(viewsets.ModelViewSet):
    queryset = StudentCertificate.objects.all()
    serializer_class = StudentCertificateSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return certificates of the logged-in student
        user = self.request.user
        if user.is_authenticated and user.role == 'student':
            return StudentCertificate.objects.filter(student=user)
        else:
            return StudentCertificate.objects.none()

    def perform_create(self, serializer):
        student = serializer.validated_data.get('student')
        if not student:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Student field is required.")
        if student.role != 'student':
            from rest_framework.exceptions import ValidationError
            raise ValidationError("The selected user is not a student.")
        # Get the certificate_file from the request
        certificate_file = self.request.FILES.get('certificate_file')

        # Save the certificate with the file


class AdminSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_classes = Course.objects.count()
        total_departments = Department.objects.count()
        total_students = CustomUser.objects.filter(role='student').count()

        total_transcript_requests = TranscriptCertificateRequest.objects.count()
        total_provisional_requests = ProvisionalResultRequest.objects.count()
        total_requests = total_transcript_requests + total_provisional_requests

        # Define pending, completed based on verification booleans
        # Pending: any of bursar_verified, hod_verified, exam_officer_approved is False
        # Completed: all True
        # Rejected: no explicit field, set to 0 for now

        transcript_pending = TranscriptCertificateRequest.objects.filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False)
        ).count()
        transcript_completed = TranscriptCertificateRequest.objects.filter(
            bursar_verified=True, hod_verified=True, exam_officer_approved=True
        ).count()

        provisional_pending = ProvisionalResultRequest.objects.filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False)
        ).count()
        provisional_completed = ProvisionalResultRequest.objects.filter(
            bursar_verified=True, hod_verified=True, exam_officer_approved=True
        ).count()

        total_pending = transcript_pending + provisional_pending
        total_completed = transcript_completed + provisional_completed
        total_rejected = 0  # No explicit rejected field

        data = {
            "total_classes": total_classes,
            "total_departments": total_departments,
            "total_students": total_students,
            "total_requests": total_requests,
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_rejected": total_rejected,
        }
        
        
        return Response(data, status=status.HTTP_200_OK)


from .serializers import FingerprintSerializer
from .models import Fingerprint

class FingerprintViewSet(viewsets.ModelViewSet):
    queryset = Fingerprint.objects.all()
    serializer_class = FingerprintSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

class TranscriptCertificateRequestViewSet(viewsets.ModelViewSet):
    queryset = TranscriptCertificateRequest.objects.all().order_by('-submitted_at')
    serializer_class = TranscriptCertificateRequestSerializer
    permission_classes = [AllowAny] # Currently allowing any access
    # permission_classes = [permissions.IsAuthenticated] # Commented out

class ProvisionalResultRequestViewSet(viewsets.ModelViewSet):
    queryset = ProvisionalResultRequest.objects.all().order_by('-submitted_at')
    serializer_class = ProvisionalResultRequestSerializer
    permission_classes = [AllowAny] # Currently allowing any access
    # permission_classes = [permissions.IsAuthenticated] # Commented out


from .serializers import StudentCertificateSerializer

class StudentCertificateViewSet(viewsets.ModelViewSet):
    queryset = StudentCertificate.objects.all()
    serializer_class = StudentCertificateSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     # Only return certificates of the logged-in student
    #     user = self.request.user
    #     return self.queryset.filter(student=user)

    def perform_create(self, serializer):
        student = serializer.validated_data.get('student')
        if not student:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Student field is required.")
        if student.role != 'student':
            from rest_framework.exceptions import ValidationError
            raise ValidationError("The selected user is not a student.")
        serializer.save()


class AdminSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_classes = Course.objects.count()
        total_departments = Department.objects.count()
        total_students = CustomUser.objects.filter(role='student').count()

        total_transcript_requests = TranscriptCertificateRequest.objects.count()
        total_provisional_requests = ProvisionalResultRequest.objects.count()
        total_requests = total_transcript_requests + total_provisional_requests

        # Define pending, completed based on verification booleans
        # Pending: any of bursar_verified, hod_verified, exam_officer_approved is False
        # Completed: all True
        # Rejected: no explicit field, set to 0 for now

        transcript_pending = TranscriptCertificateRequest.objects.filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False)
        ).count()
        transcript_completed = TranscriptCertificateRequest.objects.filter(
            bursar_verified=True, hod_verified=True, exam_officer_approved=True
        ).count()

        provisional_pending = ProvisionalResultRequest.objects.filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False)
        ).count()
        provisional_completed = ProvisionalResultRequest.objects.filter(
            bursar_verified=True, hod_verified=True, exam_officer_approved=True
        ).count()

        total_pending = transcript_pending + provisional_pending
        total_completed = transcript_completed + provisional_completed
        total_rejected = 0  # No explicit rejected field

        data = {
            "total_classes": total_classes,
            "total_departments": total_departments,
            "total_students": total_students,
            "total_requests": total_requests,
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_rejected": total_rejected,
        }
        return Response(data, status=status.HTTP_200_OK)

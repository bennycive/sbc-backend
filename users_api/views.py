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
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .serializers import StudentCertificateSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, 'role', None)
        data = self.request.data

        # Validate required fields based on role
        errors = {}

        if role == 'student':
            if not data.get('yos'):
                errors['yos'] = ['Year of Study is required for students.']
        if role != 'admin':
            if not data.get('department'):
                errors['department'] = ['Department is required for non-admin users.']

        if not data.get('nida'):
            errors['nida'] = ['NIDA is required.']
        if not data.get('phone_number'):
            errors['phone_number'] = ['Phone number is required.']

        if errors:
            raise ValidationError(errors)

        try:
            serializer.save(user=user)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower() or 'unique violation' in str(e).lower():
                raise ValidationError({'nida': ['This NIDA value already exists.']})
            else:
                raise e

    def perform_update(self, serializer):
        user = self.request.user
        role = getattr(user, 'role', None)
        data = self.request.data

        # Validate required fields based on role
        errors = {}

        if role == 'student':
            if not data.get('yos'):
                errors['yos'] = ['Year of Study is required for students.']
        if role != 'admin':
            if not data.get('department'):
                errors['department'] = ['Department is required for non-admin users.']

        if not data.get('nida'):
            errors['nida'] = ['NIDA is required.']
        if not data.get('phone_number'):
            errors['phone_number'] = ['Phone number is required.']

        if errors:
            raise ValidationError(errors)

        try:
            serializer.save()
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower() or 'unique violation' in str(e).lower():
                raise ValidationError({'nida': ['This NIDA value already exists.']})
            else:
                raise e


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


class TranscriptCertificateRequestViewSet(viewsets.ModelViewSet):
    """
    This ViewSet handles transcript and certificate requests.
    - Students can create and view their own requests.
    - Staff (bursar, HOD, etc.) can view all requests to verify them.
    """
    serializer_class = TranscriptCertificateRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Dynamically filters the queryset based on the user's role.
        """
        user = self.request.user

        # If the user is a student, show only their own requests.
        if hasattr(user, 'role') and user.role == 'student':
            return TranscriptCertificateRequest.objects.filter(user=user).order_by('-submitted_at')
        
        # If the user is a staff member (or superuser), show all requests.
        # You can add more specific role checks here if needed (e.g., 'bursar', 'hod').
        elif hasattr(user, 'role') and user.role in ['bursar', 'hod', 'exam-officer', 'admin']:
             return TranscriptCertificateRequest.objects.all().order_by('-submitted_at')

        # For any other case, return an empty queryset to be safe.
        return TranscriptCertificateRequest.objects.none()

    def perform_create(self, serializer):
        """
        Automatically associates the request with the logged-in user upon creation.
        """
        serializer.save(user=self.request.user)
class ProvisionalResultRequestViewSet(viewsets.ModelViewSet):
    """
    This ViewSet handles provisional result requests.
    - Students can create and view their own requests.
    - Staff (bursar, HOD, etc.) can view all requests to verify them.
    """
    serializer_class = ProvisionalResultRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Dynamically filters the queryset based on the user's role.
        """
        user = self.request.user

        # If the user is a student, show only their own requests.
        if hasattr(user, 'role') and user.role == 'student':
            return ProvisionalResultRequest.objects.filter(user=user).order_by('-submitted_at')
        
        # If the user is a staff member or admin, show all requests.
        elif hasattr(user, 'role') and user.role in ['bursar', 'hod', 'exam-officer', 'admin']:
             return ProvisionalResultRequest.objects.all().order_by('-submitted_at')

        # For any other case, return an empty queryset.
        return ProvisionalResultRequest.objects.none()

    def perform_create(self, serializer):
        """
        Automatically associates the request with the logged-in user upon creation.
        """
        serializer.save(user=self.request.user)
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

    def create(self, request, *args, **kwargs):
        print("Received fingerprint data:", request.data)
        return super().create(request, *args, **kwargs)



from .serializers import StudentCertificateSerializer

# class StudentCertificateViewSet(viewsets.ModelViewSet):
#     queryset = StudentCertificate.objects.all()
#     serializer_class = StudentCertificateSerializer
#     permission_classes = [AllowAny]
#     # permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # Only return certificates of the logged-in student
#         user = self.request.user
#         return self.queryset.filter(student=user)

#     def perform_create(self, serializer):
#         student = serializer.validated_data.get('student')
#         if not student:
#             from rest_framework.exceptions import ValidationError
#             raise ValidationError("Student field is required.")
#         if student.role != 'student':
#             from rest_framework.exceptions import ValidationError
#             raise ValidationError("The selected user is not a student.")
#         certificate_file = self.request.FILES.get('certificate_file')
#         if certificate_file:
#             serializer.save(certificate_file=certificate_file)
#         else:
#             serializer.save()
class StudentCertificateViewSet(viewsets.ModelViewSet):
    queryset = StudentCertificate.objects.all()
    serializer_class = StudentCertificateSerializer
    # This should be IsAuthenticated to know who the user is.
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        """
        This is the updated section.
        It now correctly shows all certificates to an admin and only
        the relevant certificates to a student.
        """
        user = self.request.user
        
        # Check the user's role to return the correct queryset.
        if hasattr(user, 'role'):
            # If the user is an admin, return all certificates.
            if user.role == 'admin':
                return self.queryset.all()
            # If the user is a student, filter by their user ID.
            elif user.role == 'student':
                return self.queryset.filter(student=user)

        # For any other user, return an empty list.
        return self.queryset.none()

    # Your original perform_create method is preserved below, unchanged.
    def perform_create(self, serializer):
        student = serializer.validated_data.get('student')
        if not student:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Student field is required.")
        if student.role != 'student':
            from rest_framework.exceptions import ValidationError
            raise ValidationError("The selected user is not a student.")
        certificate_file = self.request.FILES.get('certificate_file')
        if certificate_file:
            serializer.save(certificate_file=certificate_file)
        else:
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



class StudentFinancialsView(APIView):
    """
    View to get financial records for a specific student.
    """
    def get(self, request, user_id, format=None):
        try:
            student = CustomUser.objects.get(id=user_id, role='student')
        except CustomUser.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        payment_records = PaymentRecord.objects.filter(student=student)
        other_payment_records = OtherPaymentRecord.objects.filter(student=student)

        payment_serializer = PaymentRecordSerializer(payment_records, many=True)
        other_payment_serializer = OtherPaymentRecordSerializer(other_payment_records, many=True)

        return Response({
            "payment_records": payment_serializer.data,
            "other_payment_records": other_payment_serializer.data
        })


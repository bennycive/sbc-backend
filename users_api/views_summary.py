from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import models
from .models import CustomUser, TranscriptCertificateRequest, ProvisionalResultRequest
from colleges_api.models import Department, Course

class AdminSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Calculate total classes managed by HOD based on courses assigned to HOD's department(s)
        user = request.user
        if user.role == 'admin':
            total_classes = Course.objects.count()
            total_departments = Department.objects.count()
            total_students = CustomUser.objects.filter(role='student').count()
        elif user.role == 'hod':
            department = user.profile.department if hasattr(user, 'profile') else None
            if department:
                total_classes = Course.objects.filter(department=department).count()
                total_departments = 1  # HOD oversees one department
                total_students = CustomUser.objects.filter(role='student', profile__department=department).count()
            else:
                total_classes = 0
                total_departments = 0
                total_students = 0
        else:
            total_classes = 0
            total_departments = 0
            total_students = 0

        total_transcript_requests = TranscriptCertificateRequest.objects.count()
        total_provisional_requests = ProvisionalResultRequest.objects.count()
        total_requests = total_transcript_requests + total_provisional_requests

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

class HODSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'hod':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Assuming HOD is linked to a department
        department = user.profile.department if hasattr(user, 'profile') else None
        if not department:
            return Response({"detail": "Department not found"}, status=status.HTTP_400_BAD_REQUEST)

        total_classes = Course.objects.filter(department=department).count()
        total_students = CustomUser.objects.filter(role='student', profile__department=department).count()

        total_transcript_requests = TranscriptCertificateRequest.objects.filter(user__profile__department=department).count()
        total_provisional_requests = ProvisionalResultRequest.objects.filter(user__profile__department=department).count()
        total_requests = total_transcript_requests + total_provisional_requests

        transcript_pending = TranscriptCertificateRequest.objects.filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False),
            user__profile__department=department
        ).count()
        transcript_completed = TranscriptCertificateRequest.objects.filter(
            bursar_verified=True, hod_verified=True, exam_officer_approved=True,
            user__profile__department=department
        ).count()

        provisional_pending = ProvisionalResultRequest.objects.filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False),
            user__profile__department=department
        ).count()
        provisional_completed = ProvisionalResultRequest.objects.filter(
            bursar_verified=True, hod_verified=True, exam_officer_approved=True,
            user__profile__department=department
        ).count()

        total_pending = transcript_pending + provisional_pending
        total_completed = transcript_completed + provisional_completed
        total_rejected = 0

        data = {
            "total_classes": total_classes,
            "total_students": total_students,
            "total_requests": total_requests,
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_rejected": total_rejected,
        }
        return Response(data, status=status.HTTP_200_OK)

class BursarSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'bursar':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        total_students = CustomUser.objects.filter(role='student').count()
        total_transcript_requests = TranscriptCertificateRequest.objects.filter(bursar_verified=False).count()
        total_provisional_requests = ProvisionalResultRequest.objects.filter(bursar_verified=False).count()
        total_requests = total_transcript_requests + total_provisional_requests

        transcript_pending = TranscriptCertificateRequest.objects.filter(bursar_verified=False).count()
        transcript_completed = TranscriptCertificateRequest.objects.filter(bursar_verified=True).count()

        provisional_pending = ProvisionalResultRequest.objects.filter(bursar_verified=False).count()
        provisional_completed = ProvisionalResultRequest.objects.filter(bursar_verified=True).count()

        total_pending = transcript_pending + provisional_pending
        total_completed = transcript_completed + provisional_completed
        total_rejected = 0

        data = {
            "total_students": total_students,
            "total_requests": total_requests,
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_rejected": total_rejected,
        }
        return Response(data, status=status.HTTP_200_OK)

class StudentSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        total_transcript_requests = TranscriptCertificateRequest.objects.filter(user=user).count()
        total_provisional_requests = ProvisionalResultRequest.objects.filter(user=user).count()
        total_requests = total_transcript_requests + total_provisional_requests

        transcript_pending = TranscriptCertificateRequest.objects.filter(
            user=user
        ).filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False)
        ).count()
        transcript_completed = TranscriptCertificateRequest.objects.filter(
            user=user,
            bursar_verified=True, hod_verified=True, exam_officer_approved=True
        ).count()

        provisional_pending = ProvisionalResultRequest.objects.filter(
            user=user
        ).filter(
            models.Q(bursar_verified=False) | models.Q(hod_verified=False) | models.Q(exam_officer_approved=False)
        ).count()
        provisional_completed = ProvisionalResultRequest.objects.filter(
            user=user,
            bursar_verified=True, hod_verified=True, exam_officer_approved=True
        ).count()

        total_pending = transcript_pending + provisional_pending
        total_completed = transcript_completed + provisional_completed
        total_rejected = 0

        data = {
            "total_requests": total_requests,
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_rejected": total_rejected,
        }
        return Response(data, status=status.HTTP_200_OK)

class ExamOfficerSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'exam_officer':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        total_transcript_requests = TranscriptCertificateRequest.objects.filter(exam_officer_approved=False).count()
        total_provisional_requests = ProvisionalResultRequest.objects.filter(exam_officer_approved=False).count()
        total_requests = total_transcript_requests + total_provisional_requests

        transcript_pending = TranscriptCertificateRequest.objects.filter(exam_officer_approved=False).count()
        transcript_completed = TranscriptCertificateRequest.objects.filter(exam_officer_approved=True).count()

        provisional_pending = ProvisionalResultRequest.objects.filter(exam_officer_approved=False).count()
        provisional_completed = ProvisionalResultRequest.objects.filter(exam_officer_approved=True).count()

        total_pending = transcript_pending + provisional_pending
        total_completed = transcript_completed + provisional_completed
        total_rejected = 0

        data = {
            "total_requests": total_requests,
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_rejected": total_rejected,
        }
        return Response(data, status=status.HTTP_200_OK)

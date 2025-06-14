from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from .models import TranscriptCertificateRequest, ProvisionalResultRequest, PaymentRecord, OtherPaymentRecord
from .serializers import TranscriptCertificateRequestSerializer, ProvisionalResultRequestSerializer, PaymentRecordSerializer, OtherPaymentRecordSerializer

class IsBursarOrHodOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and (user.role in ['bursar', 'hod'] or user.is_staff or user.is_superuser)

class FinancialVerificationsView(APIView):
    permission_classes = [IsBursarOrHodOrAdmin]

    def get(self, request):
        # Return all requests from TranscriptCertificateRequest and ProvisionalResultRequest
        transcript_requests = TranscriptCertificateRequest.objects.filter(user__isnull=False).order_by('-submitted_at')
        provisional_requests = ProvisionalResultRequest.objects.filter(user__isnull=False).order_by('-submitted_at')

        transcript_serializer = TranscriptCertificateRequestSerializer(transcript_requests, many=True)
        provisional_serializer = ProvisionalResultRequestSerializer(provisional_requests, many=True)

        data = {
            "transcript_requests": transcript_serializer.data,
            "provisional_requests": provisional_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

class UpdateBursarVerificationView(APIView):
    permission_classes = [IsBursarOrHodOrAdmin]

    def post(self, request, request_type, pk):
        # request_type: 'transcript' or 'provisional'
        # pk: primary key of the request
        verified = request.data.get('verified')
        if verified is None:
            return Response({"error": "Missing 'verified' field"}, status=status.HTTP_400_BAD_REQUEST)

        if request_type == 'transcript':
            obj = get_object_or_404(TranscriptCertificateRequest, pk=pk)
        elif request_type == 'provisional':
            obj = get_object_or_404(ProvisionalResultRequest, pk=pk)
        else:
            return Response({"error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

        obj.bursar_verified = verified
        obj.save()
        return Response({"status": "success", "bursar_verified": obj.bursar_verified}, status=status.HTTP_200_OK)

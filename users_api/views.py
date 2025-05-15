from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser,AcademicYear, PaymentRecord, OtherPaymentRecord
from .serializers import CustomUserSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
import json
from django.http import JsonResponse
from rest_framework import viewsets
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer, AcademicYearSerializer,PaymentRecordSerializer,OtherPaymentRecordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from .models import TranscriptCertificateRequest, ProvisionalResultRequest
from .serializers import TranscriptCertificateRequestSerializer, ProvisionalResultRequestSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [IsAuthenticated]
        


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    # permission_classes = [IsAuthenticated]


class PaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    # permission_classes = [IsAuthenticated]


class OtherPaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = OtherPaymentRecord.objects.all()
    serializer_class = OtherPaymentRecordSerializer
    # permission_classes = [IsAuthenticated]

class TranscriptCertificateRequestViewSet(viewsets.ModelViewSet):
    queryset = TranscriptCertificateRequest.objects.all().order_by('-submitted_at')
    serializer_class = TranscriptCertificateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProvisionalResultRequestViewSet(viewsets.ModelViewSet):
    queryset = ProvisionalResultRequest.objects.all().order_by('-submitted_at')
    serializer_class = ProvisionalResultRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

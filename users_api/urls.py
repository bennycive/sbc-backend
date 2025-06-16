# users_api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomUserViewSet, ProfileViewSet, AcademicYearViewSet, PaymentRecordViewSet, OtherPaymentRecordViewSet,TranscriptCertificateRequestViewSet, ProvisionalResultRequestViewSet
from .views import StudentCertificateViewSet
from .views_financial_verifications import FinancialVerificationsView, UpdateBursarVerificationView
from .views import StudentFinancialsView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'profiles', ProfileViewSet)

router.register(r'academic-years', AcademicYearViewSet)
router.register(r'payment-records', PaymentRecordViewSet)
router.register(r'other-payment-records', OtherPaymentRecordViewSet)

router.register(r'transcript-certificate-requests', TranscriptCertificateRequestViewSet, basename='transcript-certificate-request')
router.register(r'provisional-requests', ProvisionalResultRequestViewSet, basename='provisional-request')
router.register(r'certificates', StudentCertificateViewSet, basename='studentcertificate')


from .views_mfa import *


from .views_summary import AdminSummaryView, HODSummaryView, BursarSummaryView, StudentSummaryView, ExamOfficerSummaryView

#router.register(r'fingerprints', FingerprintViewSet, basename='fingerprint')


urlpatterns = [
    
    path('', include(router.urls)),
    path('dashboard/admin/summary/', AdminSummaryView.as_view(), name='admin-summary'),
    path('dashboard/hod/summary/', HODSummaryView.as_view(), name='hod-summary'),
    path('dashboard/bursar/summary/', BursarSummaryView.as_view(), name='bursar-summary'),
    path('dashboard/student/summary/', StudentSummaryView.as_view(), name='student-summary'),
    path('dashboard/examofficer/summary/', ExamOfficerSummaryView.as_view(), name='examofficer-summary'),

    path('mfa/register/options/', MfaRegisterOptionsView.as_view(), name='mfa-register-options'),
    path('mfa/register/complete/', MfaRegisterOptionsView.as_view(), name='mfa-register-complete'),
    path('mfa/authenticate/options/', MfaAuthenticateOptionsView.as_view(), name='mfa-authenticate-options'),
    path('mfa/authenticate/complete/', MfaAuthenticateCompleteView.as_view(), name='mfa-authenticate-complete'),

    path('financial-verifications/', FinancialVerificationsView.as_view(), name='financial-verifications'),
    path('financial-verifications/<str:request_type>/<int:pk>/update-bursar/', UpdateBursarVerificationView.as_view(), name='update-bursar-verification'),
    
    path('student-financials/<int:user_id>/', StudentFinancialsView.as_view(), name='student-financials'),
    


]



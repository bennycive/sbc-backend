
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollegeViewSet, DepartmentViewSet, CourseViewSet



router = DefaultRouter()
router.register(r'colleges', CollegeViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'department/courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]



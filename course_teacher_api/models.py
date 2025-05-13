from django.db import models

from courses_api.models import Course
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class CourseTeacher(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_teachers')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_teaching')

    def __str__(self):
        return f"{self.course.name} taught by {self.teacher.username}"
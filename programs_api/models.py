from django.db import models

from departments_api.models import Department

# Create your models here.

class Program(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=255)
    yos = models.PositiveSmallIntegerField()  # yos = Years of Study

    def __str__(self):
        return f"{self.name} ({self.department.name})"   
from django.db import models

class College(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255)
    college = models.ForeignKey(College, related_name='departments', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Course(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
    ]

    CLASS_LEVEL_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]

    name = models.CharField(max_length=255)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    class_level = models.CharField(max_length=1, choices=CLASS_LEVEL_CHOICES)
    department = models.ForeignKey(Department, related_name='courses', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
from django.db import models

from sbc_backend.models import TimestampModel

# Create your models here.
class Course(TimestampModel):
    name = models.CharField(max_length=255)
    code=models.CharField(max_length=255)

    def __str__(self):
        return self.name
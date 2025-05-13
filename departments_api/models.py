from django.db import models


from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
   

    def __str__(self):
        return self.name

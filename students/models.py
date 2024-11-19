from django.db import models
from users.models import CustomUser


class Student(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='something@gmail.com')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    dob = models.DateField(null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


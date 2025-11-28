from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    school = models.CharField("Школа", max_length=255, blank=True, null=True)
    position = models.CharField("Должность", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    grade = models.PositiveSmallIntegerField("Класс", blank=True, null=True)
    school = models.CharField("Школа", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username}"

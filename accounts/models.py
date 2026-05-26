from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_code")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} — {self.code}"

class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher"
    )
    school = models.CharField("Школа", max_length=255, blank=True, null=True)
    position = models.CharField("Должность", max_length=255, blank=True, null=True)

    email_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student"
    )
    grade = models.PositiveSmallIntegerField("Класс", blank=True, null=True)
    school = models.CharField("Школа", max_length=255, blank=True, null=True)

    email_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
from django.db import models
from django.contrib.auth.models import User


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
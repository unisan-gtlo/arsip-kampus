from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        OPERATOR = "operator", "Operator"
        USER = "user", "User"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    nama = models.CharField(max_length=150, blank=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_operator_role(self):
        return self.role == self.Role.OPERATOR

    @property
    def display_name(self):
        return self.nama or self.username

    def __str__(self):
        return self.username

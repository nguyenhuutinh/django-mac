from email.policy import default
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import IndexedTimeStampedModel

from .managers import UserManager
from rest_framework import serializers


class User(AbstractBaseUser, PermissionsMixin, IndexedTimeStampedModel):
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(
        default=False, help_text=_("Designates whether the user can log into this admin " "site.")
    )
    name = models.TextField(default='', null=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.email



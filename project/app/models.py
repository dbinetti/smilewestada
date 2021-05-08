
# First-Party
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from hashid_field import HashidAutoField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

# Local
from .managers import UserManager


class Account(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    is_featured = models.BooleanField(
        default=False,
    )
    is_moderated = models.BooleanField(
        default=False,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    ZONE = Choices(
        (1, 'one', 'Zone One'),
        (2, 'two', 'Zone Two'),
        (3, 'three', 'Zone Three'),
        (4, 'four', 'Zone Four'),
        (5, 'five', 'Zone Five'),
    )
    zone = models.IntegerField(
        blank=True,
        null=True,
        choices=ZONE,
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
    )
    is_public = models.BooleanField(
        default=False,
    )
    is_volunteer = models.BooleanField(
        default=False,
    )
    comments = models.TextField(
        max_length=500,
        blank=True,
        default='',
    )
    notes = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    user = models.OneToOneField(
        'app.User',
        on_delete=models.CASCADE,
        related_name='account',
        unique=True,
    )

    def __str__(self):
        return f"{self.name}"


class School(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name}"


class Voter(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    voter_id = models.IntegerField(
        blank=False,
    )
    prefix = models.CharField(
        max_length=100,
        blank=True,
    )
    last_name = models.CharField(
        max_length=100,
        blank=False,
    )
    first_name = models.CharField(
        max_length=100,
        blank=False,
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
    )
    suffix = models.CharField(
        max_length=100,
        blank=True,
    )
    age = models.IntegerField(
        blank=False,
    )
    address = models.CharField(
        max_length=100,
        blank=False,
    )
    city = models.CharField(
        max_length=100,
        blank=False,
    )
    st = models.CharField(
        max_length=2,
        blank=False,
    )
    zipcode = models.CharField(
        max_length=5,
        blank=False,
    )
    zone = models.IntegerField(
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class User(AbstractBaseUser):
    id = HashidAutoField(
        primary_key=True,
    )
    username = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        unique=True,
    )
    data = models.JSONField(
        null=True,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default='(Unknown)',
        verbose_name="Name",
        editable=False,
    )
    email = models.EmailField(
        blank=False,
        editable=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
    ]

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.name)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

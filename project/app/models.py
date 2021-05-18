
import datetime

from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video
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
        (1, 'one', 'Zone 1'),
        (2, 'two', 'Zone 2'),
        (3, 'three', 'Zone 3'),
        (4, 'four', 'Zone 4'),
        (5, 'five', 'Zone 5'),
        (6, 'outside', 'Outside District'),
    )
    zone = models.IntegerField(
        blank=True,
        null=True,
        choices=ZONE,
    )
    ROLE = Choices(
        (1, 'parent', 'Parent'),
        (2, 'student', 'Student'),
        (3, 'teacher', 'Teacher'),
        (4, 'other', 'Other'),
    )
    role = models.IntegerField(
        blank=True,
        null=True,
        choices=ROLE,
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
    is_speaker = models.BooleanField(
        default=False,
    )
    is_signage = models.BooleanField(
        default=False,
    )
    is_voter = models.BooleanField(
        default=False,
    )
    is_attending = models.BooleanField(
        default=False,
    )
    sendgrid = models.JSONField(
        null=True,
        blank=True,
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


class Assignment(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    date = models.DateField(
        default=datetime.date.today,
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.SET_NULL,
        related_name='assignments',
        null=True,
        blank=True,
    )
    school = models.ForeignKey(
        'app.School',
        on_delete=models.CASCADE,
        related_name='assignments',
        null=False,
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return f"{self.id}"


class Attendee(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.SET_NULL,
        related_name='attendees',
        null=True,
        blank=False,
    )
    event = models.ForeignKey(
        'app.Event',
        on_delete=models.SET_NULL,
        related_name='attendees',
        null=True,
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return f"{self.id}"


class Discussion(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    date = models.DateField(
        default=datetime.date.today,
    )
    video = models.FileField(
        upload_to='videos/',
        blank=True,
        storage=VideoMediaCloudinaryStorage(),
        validators=[validate_video],
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return f"{self.id}"


class Event(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    date = models.DateField(
        default=datetime.date.today,
    )
    location = models.CharField(
        max_length=100,
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
        editable=True,
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

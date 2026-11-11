# coding=utf-8
from django.db import models
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, is_password_usable
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    '''custom user model inherited from default Django AUTH User model'''

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    # regular expression: all number, total 8 digits, use for validate phone number input
    phone_regex = RegexValidator(
        regex=r"^\d{8}$",  # Exactly 8 digits
        message=_("Phone number must be 8 digits."),
    )

    # add phone number as extra field
    # Use the regex validator above to check if the inputed phone number is number and total 8 digits
    phone_number = models.CharField(
        max_length=8,
        unique=True,
        validators=[phone_regex],
        null=True, blank=True,
        error_messages={"unique": _("A user with that phone number already exists."),},
    )

    # make email field to be unique, default django auth allow duplicated email address
    email = models.EmailField(
        max_length=60,
        unique=True,
        error_messages={"unique": _("A user with that email address already exists."),},
    )

    # now when create an user account, it requires email too. Note: username is always required by Django
    REQUIRED_FIELDS = ["email"]

    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modified_users'
    )
    is_user = models.BooleanField(
        default = False,
        verbose_name = _('IS USER'),
    )
    is_admin = models.BooleanField(
        default = False,
        verbose_name = _('IS ADMIN'),
    )

    def save(self, *args, request=None, **kwargs):
        '''
        Custom save method to handle password hashing, date/time create/update,
        and setting the 'modified_by' field.
        '''
        # save the modified date
        self.date_modified = timezone.now()

        # Hash the password if it's not already hashed
        # is_password_usable() returns False for already-hashed passwords
        if self.password and not is_password_usable(self.password):
            self.password = make_password(self.password)

        # Save the modified_by field if a request is provided and the user is authenticated.
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.modified_by = request.user
        elif self.pk is not None and self.modified_by is None:
            # handle the case where a user is being edited from admin interface, or a system process
            # if a user is being edited and modified_by is None, set it to itself.
            self.modified_by = self

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.phone_number})"


class Profile(models.Model):
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('lo', _('Lao')),
    ] # 'en' or 'lo' is the value stored in the databas not English or Lao

    COLOR_CHOICES = [
        ('w3-theme-dark.css', _('dark')),
        ('w3-theme-black.css', _('black')),
        ('w3-theme-blue.css', _('blue')),
        ('w3-theme-light-blue.css', _('light blue')),
        ('w3-theme-blue-grey.css', _('blue grey')),
        ('w3-theme-red.css', _('red')),
        ('w3-theme-brown.css', _('brown')),
        ('w3-theme-cyan.css', _('cyan')),
        ('w3-theme-grey.css', _('grey')),
        ('w3-theme-dark-grey.css', _('dark grey')),
        ('w3-theme-orange.css', _('orange')),
        ('w3-theme-deep-orange.css', _('deep orange')),
        ('w3-theme-purple.css', _('purple')),
        ('w3-theme-deep-purple.css', _('deep purple')),
        ('w3-theme-green.css', _('green')),
        ('w3-theme-light-green.css', _('light green')),
        ('w3-theme-indigo.css', _('indigo')),
        ('w3-theme-khaki.css', _('khaki')),
        ('w3-theme-lime.css', _('lime')),
        ('w3-theme-pink.css', _('pink')),
        ('w3-theme-teal.css', _('teal')),
        ('w3-theme-yellow.css', _('yellow')),
        ('w3-theme-amber.css', _('amber')),
    ]

    # 1-to-1 relationship this Profile model to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme_color = models.CharField(max_length=50, choices=COLOR_CHOICES, default='w3-theme-blue.css')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')

    def __str__(self):
        return 'Profile of {}'.format(self.user.username)

    def user_email(self):
        return self.user.email

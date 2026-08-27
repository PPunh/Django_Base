# coding=utf-8
from django.db import models
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, is_password_usable
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    '''custom user model inherited from default Django AUTH User model'''

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # regular expression: all number, total 8 digits, use for validate phone number input
    phone_regex = RegexValidator(
        regex=r"^\d{8}$",  # Exactly 8 digits
        message="Phone number must be 8 digits.",
    )

    # add phone number as extra field
    # Use the regex validator above to check if the inputed phone number is number and total 8 digits
    phone_number = models.CharField(max_length=8, unique=True, validators=[phone_regex],
        null=True, blank=True, error_messages={"unique": "A user with that phone number already exists.",},)

    # make email field to be unique, default django auth allow duplicated email address
    email = models.EmailField(max_length=60, unique=True,
        error_messages={"unique": "A user with that email address already exists.",},)

    # now when create an user account, it requires email too. Note: username is always required by Django
    REQUIRED_FIELDS = ["email"]

    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modified_users'
    )
    is_sale = models.BooleanField(
        default = False,
        verbose_name = 'IS SALE',
        help_text = 'Designates whether the user belongs to the SALE team.'
    )
    is_finance = models.BooleanField(
        default = False,
        verbose_name = 'IS FINANCE',
        help_text = 'Designates whether the user belongs to the FINANCE team.'
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
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('lo', 'Lao'),
    ] # 'en' or 'lo' is the value stored in the databas not English or Lao

    COLOR_CHOICES = [
        ('w3-theme-blue.css', 'blue'),
        ('w3-theme-light-blue.css', 'light blue'),
        ('w3-theme-blue-grey.css', 'blue grey'),
        ('w3-theme-red.css', 'red'),
        ('w3-theme-brown.css', 'brown'),
        ('w3-theme-cyan.css', 'cyan'),
        ('w3-theme-grey.css', 'grey'),
        ('w3-theme-dark-grey.css', 'dark grey'),
        ('w3-theme-orange.css', 'orange'),
        ('w3-theme-deep-orange.css', 'deep orange'),
        ('w3-theme-purple.css', 'purple'),
        ('w3-theme-deep-purple.css', 'deep purple'),
        ('w3-theme-green.css', 'green'),
        ('w3-theme-light-green.css', 'light green'),
        ('w3-theme-indigo.css', 'indigo'),
        ('w3-theme-khaki.css', 'khaki'),
        ('w3-theme-lime.css', 'lime'),
        ('w3-theme-pink.css', 'pink'),
        ('w3-theme-teal.css', 'teal'),
        ('w3-theme-yellow.css', 'yellow'),
    ]

    # 1-to-1 relationship this Profile model to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme_color = models.CharField(max_length=50, choices=COLOR_CHOICES, default='w3-theme-blue.css')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')

    def __str__(self):
        return 'Profile of {}'.format(self.user.username)

    def user_email(self):
        return self.user.email
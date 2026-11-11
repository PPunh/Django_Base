# coding=utf-8
import os
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from apps.users.middleware import get_current_user

class Province(models.Model):
    PROVINCE_CHOICE = [
        ('Phongsaly', _('Phongsaly')),
        ('Luangnamtha', _('Luangnamtha')),
        ('Borkeo', _('Borkeo')),
        ('Oudomxay', _('Oudomxay')),
        ('Xayaburi', _('Xayaburi')),
        ('Luangprabang', _('Luangprabang')),
        ('Houaphan', _('Houaphan')),
        ('Xiangkhouang', _('Xiangkhouang')),
        ('Vientiane Province', _('Vientiane Province')),
        ('Vientiane Capital', _('Vientiane Capital')),
        ('Xaisomboun', _('Xaisomboun')),
        ('Borlikhamxai', _('Borlikhamxai')),
        ('Khammouan', _('Khammouan')),
        ('Salavan',_('Salavan')),
        ('Champasak', _('Champasak')),
        ('Attapeu', _('Attapeu')),
    ]
    name = models.CharField(
        max_length=50,
        choices=PROVINCE_CHOICE,
        verbose_name=_("Province"))

    class Meta:
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')
        ordering = ['id']

    def __str__(self):
        return str(self.get_name_display())


class PersonalInfoModel(models.Model):
    """
    Base personal infomation for other apps
    """
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    surname = models.CharField(max_length=50, verbose_name=_("Surname"))
    phone_regex = RegexValidator(
        regex=r"^\d{8}$",  # Exactly 8 digits
        message= _ ("Phone number must be exactly 8 digits")
    )
    phone_number = models.CharField(
        max_length=8,
        validators=[phone_regex],
        verbose_name=_("Phone Number")
    )
    address = models.CharField(max_length=200, verbose_name=_("Address"))
    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        verbose_name=_("Province"),
        blank=True, null=True
    )

    class Meta:
        verbose_name = _("Personal Information")
        verbose_name_plural = _("Personal Information")

    def __str__(self):
        return f"{self.name} {self.surname}"


class PictureModel(models.Model):
    profile_picture = models.ImageField(
        upload_to='profiles/',
        verbose_name=_("Profile Picture"),
        blank=True, null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Check if the instance is being updated (not created)
        if self.pk:
            old_obj = self.__class__.objects.get(pk=self.pk)
            if self.profile_picture and self.profile_picture != old_obj.profile_picture:
                self.profile_picture = utils.compress_image(self.profile_picture)
        else:
            # Case when creating new instance
            if self.profile_picture:
                self.profile_picture = utils.compress_image(self.profile_picture)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Store file in variable to delete after super().delete() success
        storage_profile = self.profile_picture

        super().delete(*args, **kwargs)

        # Delete file from Storage (Support both Local and Cloud)
        if storage_profile:
            storage_profile.delete(save=False)


class AutiTableModel(models.Model):
    """
    Abtrac table models for provide common fields of Created_by, Created_date, Modified_by, Modified_date
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name = _("Created By"),
        related_name="%(class)s_created_by"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created Date")
    )

    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name = _("Modified By"),
        related_name="%(class)s_modified_by"
    )
    modified_at = models.DateTimeField(
        auto_now = True,
        verbose_name = _("Modified Date")

    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Enhance save mothod with automatically set created_by and modified_by
        """
        user = kwargs.pop('user', None)

        if not user:
            user = get_current_user()

        # Set Created_by
        if not self.pk and user and user.is_authenticated:
            self.created_by = user

        # Always Upsate modified_by when user is availabke
        if user and user.is_authenticated:
            self.modified_by = user

        super().save(*args, **kwargs)

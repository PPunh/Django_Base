# coding=utf-8
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from apps.users.middleware import get_current_user


class Province(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Province")
    )

    def __str__(self):
        return self.name


class District(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name=_("Province")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("District")
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['province', 'name'], name='unique_district_per_province')
        ]

    def __str__(self):
        return self.name


class Address(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Province")
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("District")
    )
    village = models.CharField(
        max_length=100,
        verbose_name=_("Village")
    )

    class Meta:
        abstract = True

    @property
    def full_address(self):
        parts = [
            self.village,
            str(self.district) if self.district else "",
            str(self.province) if self.province else "",
        ]
        return ", ".join(filter(None, parts))


class PersonalInfoModel(Address):
    """
    Base personal information for other apps
    """
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    surname = models.CharField(max_length=50, verbose_name=_("Surname"))
    phone_regex = RegexValidator(
        regex=r"^\d{8}$",
        message=_("Phone number must be exactly 8 digits")
    )
    phone_number = models.CharField(
        max_length=8,
        validators=[phone_regex],
        verbose_name=_("Phone Number")
    )
    email = models.EmailField(
        max_length=60,
        verbose_name=_("Email"),
        unique=True,
        blank=True,
        null=True,
        error_messages={"unique": _("A user with that email address already exists.")},
    )

    class Meta(Address.Meta):
        abstract = True
        verbose_name = _("Personal Info")
        verbose_name_plural = _("Personal Info")

    def __str__(self):
        return f"{self.name} {self.surname}"


class AuditTableModel(models.Model):
    """
    Abstract table model providing common fields: created_by, created_at, modified_by, modified_at
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Created By"),
        related_name="%(class)s_created_by"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created Date")
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Modified By"),
        related_name="%(class)s_modified_by"
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modified Date")
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None) or get_current_user()

        if self._state.adding and user and user.is_authenticated:
            self.created_by = user

        if user and user.is_authenticated:
            self.modified_by = user

        super().save(*args, **kwargs)

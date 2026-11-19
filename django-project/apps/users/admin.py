# coding=utf-8
from django.contrib import admin
from django.utils import timezone
#from django.contrib.auth.admin import UserAdmin
from . import models
from . import forms


class ProfileAdmin(admin.ModelAdmin):
    model = models.Profile

class ProfileInline(admin.StackedInline):  # Or admin.TabularInline for a more compact view
    model = models.Profile
    can_delete = False  # Prevent deleting the profile directly from the user admin

class PersonalInfoInline(admin.StackedInline):
    model = models.PersonalInfo
    fk_name = "user"
    can_delete = False
    extra = 0

    class Media:
        js = ('common/js/chained_address.js',)

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    model = models.User
    inlines = (
        ProfileInline,
        PersonalInfoInline,
    )

    class Media:
        js = ('common/js/chained_address.js',)

    def display_modified(self, obj): # display modified in local time
        return timezone.localtime(obj.date_modified).strftime('%Y-%m-%d %H:%M')

    display_modified.short_description = "Modified" #Set the column header

    list_display = (
        'username',
        'email',
        'phone_number',
        'display_modified',
        'modified_by'
    )

admin.site.register(models.Profile)

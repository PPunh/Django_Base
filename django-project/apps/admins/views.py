# coding=utf-8
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from apps.users.models import User, Profile, PersonalInfo
from apps.users.forms import UserUpdateForm, ProfileForm, PersonalInfoForm
from apps.common.mixins import MultipleInlineFormsetMixin

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "admins/profile.html"
    context_object_name = "user_obj"

    def get_object(self, queryset=None):
        return (
            User.objects.select_related(
                "profile",
                "personal_info"
            ).get(pk=self.request.user.pk)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Profile")
        return context


class ProfileUpdateView(LoginRequiredMixin, MultipleInlineFormsetMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "admins/update_profile.html"
    context_object_name = "user_obj"

    inline_formsets = [
        {
            'model': Profile,
            'form': ProfileForm,
            'extra': 1,
            'max_num': 1,
            'can_delete': False,
            'fk_name': 'user',
            'formset_name': 'user_profile_formset',
        },
        {
            'model': PersonalInfo,
            'form': PersonalInfoForm,
            'extra': 1,
            'max_num': 1,
            'can_delete': False,
            'fk_name': 'user',
            'formset_name': 'user_personal_info_formset',
        },
    ]

    def get_object(self, queryset=None):
        return (
            User.objects.select_related(
                "profile",
                "personal_info"
            ).get(pk=self.request.user.pk)
        )

    def get_success_url(self):
        messages.success(
            self.request,
            _("Update account successful")
        )
        return reverse_lazy(
            'admins:profile_home',
            # kwargs = {
            #     'pk':self.object.pk
            # }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Update Profile")
        return context

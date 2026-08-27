from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .backends import MultiAuthBackend
from django.utils import timezone
from . import models
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100, 
        label="Username / Email / Phone number"
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Let Django's AuthenticationForm handle authentication.
        It will automatically use all configured backends (including MultiAuthBackend)
        and properly pass self.request to authenticate().
        """
        return super().clean()


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
            'is_active',
            'is_sale',
            'is_finance',
            'is_superuser',
            # 'is_staff',
        ]
        labels = {
            'username': 'Username',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'password1': 'Password',
            'password2': 'Confirm Password',
            'is_active': 'Active',
            'is_sale':'Is Sale',
            'is_finance':'Is Finance',
            'is_superuser': 'Superuser',
            # 'is_staff': 'Staff',
        }
        widgets = {
            'is_superuser': forms.CheckboxInput(
                attrs={
                    'class': 'w3-check',
                }
            ),
            'is_sale': forms.CheckboxInput(
                attrs={
                    'class': 'w3-check',
                }
            ),
            'is_finance': forms.CheckboxInput(
                attrs = {
                    'class':'w3-check',
                }
            ),
            # 'is_staff': forms.CheckboxInput(
            #     attrs={
            #         'class': 'w3-check',
            #     }
            # ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'w3-check',
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        css_class = 'form-control w3-input w3-borderw3-margin-bottom'

        for field in self.fields.values():
            field.widget.attrs['class']= f"{field.widget.attrs.get('class', '')} {css_class}".strip()
            field.help_text = None


class SuperUserCreationForm(forms.ModelForm):
    """
        Form for creating SUPPERUSRE
    """
    password1 = forms.CharField(
        label = 'Password',
        strip = False,
        widget = forms.PasswordInput(attrs = {"autocomplete":'Password'}),
        validators = [validate_password]
    )
    password2 = forms.CharField(
        label = 'Confirm Password',
        strip = False,
        widget = forms.PasswordInput(attrs={"autocomplete":'Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone_number")

    def clean(self):
        """Validate that password1 and password2 match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Check if user input password1, password2 and both match
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                'Passwords do not match.'
            )
        return cleaned_data
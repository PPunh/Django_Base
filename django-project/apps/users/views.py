import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django_ratelimit.decorators import ratelimit

from . import forms
from . import models
from . models import User
from .forms import CustomUserForm, SuperUserCreationForm

# LOGGER
logger = logging.getLogger(__name__)

# LoginView
class Login(LoginView):
    '''user login using class base view (CBV)'''

    form_class = AuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        if not models.User.objects.filter(is_superuser=True).exists():
            return redirect("users:create_super")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get the default context provided by LoginView
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'  # Add custom context
        return context

    # redirect to page when login successful
    def get_success_url(self):
        return reverse_lazy('users:home')

    def form_valid(self, form):
        # Only show the welcome message on a real login submission
        messages.success(self.request, 'You have successfully logged in')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Username / Email / Phone number / Password is required')
        return super().form_invalid(form)  # Re-render the form with errors message

class Home(TemplateView):
    template_name = "users/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        return context


@never_cache
@require_http_methods(["GET", "POST"])
@ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True)
def logout_view(request):
    theme = request.session.get('theme_color')
    if request.user.is_authenticated:
        theme = (
            models.Profile.objects.filter(user=request.user)
            .values_list('theme_color', flat=True)
            .first()
            or theme
        )

    logout(request)
    if theme in {color for color, _ in models.Profile.COLOR_CHOICES}:
        request.session['theme_color'] = theme
    messages.success(request, 'You have successfully logged out')
    return redirect('users:login')


@require_http_methods(["GET", "POST"])
def set_theme(request):
    """
    Switch theme preference.
    Can be called via GET query ?theme=w3-theme-red.css or POST.
    Updates the session, and if user is logged in, saves to Profile.
    """
    theme = request.GET.get('theme') or request.POST.get('theme')
    valid_themes = [choice[0] for choice in models.Profile.COLOR_CHOICES]

    if theme and theme in valid_themes:
        request.session['theme_color'] = theme
        if request.user.is_authenticated:
            try:
                profile, _ = models.Profile.objects.get_or_create(user=request.user)
                profile.theme_color = theme
                profile.save(update_fields=['theme_color'])
            except Exception as e:
                logging.getLogger(__name__).warning("Failed to save theme to profile: %s", e)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('users:home' if request.user.is_authenticated else 'users:login')



class SuperUserCreation(FormView):
    """
        Using for Create First SuperUser
    """
    template_name = "users/createsuperuser.html"

    def get_success_url(self):
        messages.success(
            self.request,
            'Created SuperUser successfully.'
        )
        return reverse_lazy(
            "users:login"
        )

    def get(self, request, *args, **kwargs):
        # Check if any super already exists
        if models.User.objects.filter(is_superuser = True).exists():
            return HttpResponse(
                "<br><h2>The system already has an existing superuser \
                and is not allowed to create another using this interface.</h2>"
            )

        # Initialize both forms
        user_form = forms.SuperUserCreationForm()

        context = {
            'title' : "Create First Superuser",
            'user_form' : user_form,
        }

        return render(
            request, self.template_name, context
        )

    # Create a Super User
    def post(self, request, *args, **kwargs):
        # Check if any superuser already exists (repeat for POST Request)
        if models.User.objects.filter(is_superuser = True).exists():
            return HttpResponse(
                "<br><h2>The system already has an existing superuser \
                and is not allowed to create another using this interface.</h2>"
            )

        user_form = forms.SuperUserCreationForm(request.POST)

        if user_form.is_valid():
            # Use create_user() which handles password hashing correctly
            models.User.objects.create_user(
                username=user_form.cleaned_data["username"],
                email=user_form.cleaned_data["email"],
                phone_number=user_form.cleaned_data["phone_number"],
                password=user_form.cleaned_data["password1"],
                is_superuser=True,
                is_staff=True,
                is_active=True
            )

            return redirect(self.get_success_url())

        context = {
            'title' : "Create First Superuser",
            'user_form' : user_form,
        }
        return render(
            request, self.template_name, context
        )

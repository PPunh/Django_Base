from django.http import HttpResponse
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic import ListView, TemplateView
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit
from django.conf import settings
from django.utils import timezone

from . import forms
from . import models
from . models import User
from .forms import CustomUserForm, SuperUserCreationForm

# LOGGER
logger = logging.getLogger(__name__)

# LoginView
@method_decorator(never_cache, name='dispatch')
@method_decorator(ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True), name='dispatch')
class Login(LoginView):
    '''user login using class base view (CBV)'''

    form_class = AuthenticationForm
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        if not models.User.objects.filter(is_superuser=True).exists():
            return redirect("users:create_super")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get the default context provided by LoginView
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'  # Add custom context
        context['theme_color'] = 'w3-theme-blue.css'
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

@method_decorator(
    ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True),
    name='dispatch',
)
class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        return context


@never_cache
@require_http_methods(["GET", "POST"])
@ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True)
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('users:login')


@method_decorator(
    ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True),
    name='dispatch'
)
class SuperUserCreation(FormView):
    """
        Using for Create First SuperUser
    """
    template_name = "createsuperuser.html"

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
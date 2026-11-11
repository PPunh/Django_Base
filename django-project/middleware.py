from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, resolve_url
from django_ratelimit.exceptions import Ratelimited


class CustomRateLimitMeaage:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return HttpResponse(
                "<h3>You've exceeded the rate limit at 100 requests per minute, "
                "please try again later.</h3>",
                status=429,
            )
        return None


class BaseLoginRequiredMiddleware:
    """
    บังคับให้ทุกหน้าต้อง login ยกเว้น
      1. view ที่ติด @login_exempt
      2. url name ใน settings.LOGIN_EXEMPT_URL_NAMES   (เช่น "users:login")
      3. namespace ใน settings.LOGIN_EXEMPT_NAMESPACES (เช่น "api_public")
      4. หน้า LOGIN_URL เอง (กัน redirect loop)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_names = set(getattr(settings, "LOGIN_EXEMPT_URL_NAMES", []))
        self.exempt_namespaces = set(getattr(settings, "LOGIN_EXEMPT_NAMESPACES", []))

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            return None

        if getattr(view_func, "login_exempt", False):
            return None

        # แปลง LOGIN_URL (ชื่อ url / path / reverse_lazy) ให้เป็น path string
        login_path = str(resolve_url(settings.LOGIN_URL))

        # กัน loop: อยู่ที่หน้า login แล้วไม่ต้อง redirect
        if request.path == login_path:
            return None

        match = request.resolver_match
        if match:
            if match.view_name in self.exempt_names:
                return None
            if match.namespace in self.exempt_namespaces:
                return None

        query = urlencode({"next": request.get_full_path()})
        return redirect(f"{login_path}?{query}")

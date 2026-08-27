# coding = utf-8
import re
import logging
from threading import local
from urllib.parse import quote
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import REDIRECT_FIELD_NAME

logger = logging.getLogger(__name__)
_thread_local = local()


class CurrentUserMiddleware:
    """
    Middleware to set the current request user in thread-local storage
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.user = getattr(request, 'user', None)
        response = self.get_response(request)
        return response

def get_current_user():
    """
    Get the current request user from thread-local storage
    Return None if not found
    """
    return getattr(_thread_local, 'user', None)
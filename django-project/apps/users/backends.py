from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate
from .models import User


class MultiAuthBackend(ModelBackend):
    '''
    custom Authentication so that we can login using
    username/password or email/password or phone_number/password
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or password is None:
            return None

        if "@" in username:  # Treat as email
            kwargs = {'email': username}
        elif username.isdigit(): # Treat as phone number
            kwargs = {'phone_number': username}
        else: # Treat as username
            kwargs = {'username': username}

        try:
            user = User.objects.get(**kwargs)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        # Do not allow authentication of inactive users (same as ModelBackend)
        if not self.user_can_authenticate(user):
            return None

        if user.check_password(password):
            return user
        return None

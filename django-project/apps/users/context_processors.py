from .models import Profile


def theme_context(request):
    """
    Context processor to provide the active theme_color and available_themes
    globally to all templates.

    Resolution order:
    1. Authenticated user's Profile.theme_color (if profile exists)
    2. request.session['theme_color'] (for guests or quick session switch)
    3. Default: 'w3-theme-blue.css'
    """
    theme = None
    if getattr(request, 'user', None) and request.user.is_authenticated:
        try:
            profile = getattr(request.user, 'profile', None)
            if profile and profile.theme_color:
                theme = profile.theme_color
        except Exception:
            pass

    if not theme:
        theme = request.session.get('theme_color', 'w3-theme-blue.css')

    return {
        'theme_color': theme,
        'available_themes': Profile.COLOR_CHOICES,
    }


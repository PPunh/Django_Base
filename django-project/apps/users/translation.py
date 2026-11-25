from modeltranslation.translator import register, TranslationOptions
from apps.users.models import PersonalInfo

@register(PersonalInfo)
class PersonalInfoTranslation(TranslationOptions):
    fields = ("village", "name", "surname")

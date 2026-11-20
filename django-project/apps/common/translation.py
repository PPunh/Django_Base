from modeltranslation.translator import register, TranslationOptions
from apps.common.models import Province, District

@register(Province)
class ProvinceTranslation(TranslationOptions):
    fields = ("name", )

@register(District)
class DistrictTranslation(TranslationOptions):
    fields = ("name", )

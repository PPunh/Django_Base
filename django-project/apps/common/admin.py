from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.common.models import Province, District

@admin.register(Province)
class ProvinceAdmin(TabbedTranslationAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(District)
class DistrictAdmin(TabbedTranslationAdmin):
    list_display = ['id', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name']

class BaseAddressAdmin(admin.ModelAdmin):
    class Media:
        js = ('common/js/chained_address.js',)

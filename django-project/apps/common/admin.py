from django.contrib import admin
from apps.common.models import Province, District, PersonalInfoModel
from apps.common.forms import PersonalInfoAdminForm

@admin.register(PersonalInfoModel)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'phone_number', "village", "district", "province",)
    search_fields = ('phone_number', 'name')
    form = PersonalInfoAdminForm

    class Media:
        js = ('common/js/chained_address.js',)

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name']

class BaseAddressAdmin(admin.ModelAdmin):
    class Media:
        js = ('common/js/chained_address.js',)

# coding=utf-8
from django import forms
from apps.common.models import District, PersonalInfoModel

class ChainedAddressFormMixin:
    province_field = 'province'
    district_field = 'district'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.province_field in self.fields and self.district_field in self.fields:
            self.fields[self.district_field].queryset = District.objects.none()

            if self.province_field in self.data:
                try:
                    province_id = int(self.data.get(self.province_field))
                    self.fields[self.district_field].queryset = District.objects.filter(
                        province_id=province_id
                    ).order_by('name')
                except (ValueError, TypeError):
                    pass
            elif getattr(self.instance, 'pk', None):
                province_obj = getattr(self.instance, self.province_field, None)
                if province_obj:
                    self.fields[self.district_field].queryset = District.objects.filter(
                        province=province_obj
                    ).order_by('name')


class PersonalInfoAdminForm(ChainedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = PersonalInfoModel
        fields = '__all__'

# coding=utf-8
import json

from django.test import TestCase
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from .admin import PersonalInfoAdmin
from .models import District, PersonalInfoModel, Province
from .views import load_districts


class ChainedAddressAdminTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(name='Province A')
        self.other_province = Province.objects.create(name='Province B')
        self.district = District.objects.create(name='District A', province=self.province)
        self.other_district = District.objects.create(name='District B', province=self.other_province)

    def test_personal_info_admin_loads_address_script_and_filters_districts(self):
        model_admin = admin.site._registry[PersonalInfoModel]
        self.assertIsInstance(model_admin, PersonalInfoAdmin)
        self.assertIn('common/js/chained_address.js', model_admin.media._js)

        request = RequestFactory().get('/admin/')
        request.user = AnonymousUser()
        form_class = model_admin.get_form(request)
        form = form_class(data={
            'name': 'Test',
            'surname': 'User',
            'phone_number': '12345678',
            'village': 'Village',
            'province': self.province.pk,
            'district': self.other_district.pk,
        })

        self.assertEqual(list(form.fields['district'].queryset), [self.district])
        self.assertFalse(form.is_valid())

    def test_load_districts_returns_only_districts_in_selected_province(self):
        request = RequestFactory().get(
            '/common/ajax/load-districts/',
            {'province_id': self.province.pk},
        )

        response = load_districts(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            [{'id': self.district.pk, 'name': self.district.name}],
        )

    def test_load_districts_without_province_returns_empty_list(self):
        response = load_districts(RequestFactory().get('/common/ajax/load-districts/'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

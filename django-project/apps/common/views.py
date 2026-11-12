# coding=utf-8
from django.http import JsonResponse
from django.views.generic import CreateView
from .models import District, Address
from .forms import ChainedAddressFormMixin

def load_districts(request):
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse([], safe=False)

    districts = District.objects.filter(province_id=province_id).values('id', 'name').order_by('name')
    return JsonResponse(list(districts), safe=False)

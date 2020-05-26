from django.http import JsonResponse
from .codes import Codes


def get_codes_ajax(request, code, filter_text=None):
    resp = {}
    if code in ('state', 'country'):
        resp = Codes().get_codes(code, filter_text=filter_text)
    elif code == 'county':
        resp = Codes().get_county_codes(filter_text=filter_text)

    return JsonResponse(resp)

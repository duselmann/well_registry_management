from django.http import JsonResponse


def get_codes_ajax(request, code):
    resp = {'foo': code}
    return JsonResponse(resp)

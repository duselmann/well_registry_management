import logging
from django.http import JsonResponse
from .codes import Codes

LOG = logging.getLogger("lookups_views")


def get_codes_ajax(request, code, filter_text=None):
    """Handles the request for JSON codes."""
    resp = {}

    if code in ('state', 'country'):
        resp = Codes().get_codes(code, filter_text=filter_text)
    elif code == 'county':
        # have to call this separate if we want the label order reversed
        resp = Codes().get_county_codes(filter_text=filter_text)
    LOG.debug("ajax request: %s %s", code, filter_text)

    return JsonResponse(resp)

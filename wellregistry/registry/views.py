"""
Registry application views.
"""
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from lookups.codes import Codes


class BasePage(TemplateView):
    """
    Landing page.

    """
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        codes = Codes()

        context = {
            'country_codes': {
                'id':    'country_selection_id',
                'name':  'country_form_name',
                'label': 'Country',
                'na':    True,
                'hint':  'Select a Country',
                'codes': codes.get_country_codes(),
            },
            'county_codes': {
                'id': 'county_selection_id',
                'name': 'county_form_name',
                'label': 'County',
                'na': True,
                'hint': 'Select a County',
                'codes': codes.get_county_codes('Wisconsin'),
            },
            'state_codes': {
                'id': 'state_selection_id',
                'name': 'state_form_name',
                'label': 'State',
                'na': True,
                'hint': 'Select a State',
                'codes': codes.get_state_codes('US'),
            },
        }

        return context


def status_check(request):
    """
    JSON response for health checks.

    """
    # because the argument is framework we will ignore
    # pylint: disable=unused-argument
    resp = {'status': 'up'}
    return JsonResponse(resp)

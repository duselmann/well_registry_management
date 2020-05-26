"""
Register Django URL route names.
"""
from django.urls import path

from .views import get_codes_ajax


urlpatterns = [
    path('<code>', get_codes_ajax, name='get_codes_ajax'),
    path('<code>/<filter_text>', get_codes_ajax, name='get_codes_ajax'),
]

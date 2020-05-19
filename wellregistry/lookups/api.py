"""
Various code lookup methods that are pointing to WQP services end points.

Currently country, state, and county are supplied by WQP. However, WQP
database also contains other potential code lookup tables that are not
exposed as service endpoints. WQP has tables for national aquifers,
altitude datum, and location datum that would be ideal for this product.

NGWMN also has a units code lookup that WQP does not have. It might be
nice to add the units table to the WQP database and expose a service
for lookup encapsulation. The table will have to be migrated someplace,
either in the registry app or WQP. If in WQP then it would follow the
same pattern instead of a unique impl for one lookup value.

"""
import requests
from xml.etree import ElementTree
from .cache import UrlContentCache
from django.conf import settings

# TODO what is the persistence of these global instances and what is the Django why
CACHE = UrlContentCache()
DURATION = settings.Environment['LOOKUP_VALUES_CACHE_DURATION']


def get_country_codes(filter_text=None):
    """
    Lookup the country codes present in the service endpoint.

    filter_text is a text string the refines the response collection.
    While it is available, it is actually unlikely that the filter will
    be provided for country because of two reasons.
    1) There are relatively few country codes that filtering minimally useful.
    2) This is the top level of location. It is the most general.

    :param filter_text: any text used to reduce the response count.
    :return: a dictionary of country codes and descriptions

    """
    return get__codes('country', filter_text)


def get_county_codes(country=None, state=None):
    """
    Lookup the collection of county codes present in the service endpoint reduced by the filter text.

    The number of county is relatively large and contains codes to filter on country and state.
    If a country and state are provided then it is able to reduce the response collection to those
    most relevant to the input. It is likely that the country and state have already been selected.

    :param country: country code or name used to reduce the counties in that country.
    :param state:   state code or name used to reduce the counties in that state or province.
    :return: a dictionary of county codes and descriptions

    """
    filter_text = f"{country}:{state}" if country is not None or state is not None else ""
    return get__codes('county', filter_text)


def get_state_codes(filter_text=None):
    """
    Lookup the collection of state codes present in the service endpoint reduced by the filter text.

    The most likely filter text will be a country code. However, the service endpoint is more flexible.
    Additionally, the service currently only provides US state codes.

    :param filter_text: country code, name, or other text used
        to reduce codes within that country or pattern match.
    :return: a dictionary of state codes and descriptions

    """
    return get__codes('state', filter_text)


def get__codes(code_type, filter_text=None):
    """
    General codes lookup method.

    :param code_type:   The endpoint code lookup name. Current valid values are
        countrycode, statecode, and countycode. This helper method appends 'code'
        to the URL code type.
    :param filter_text: optional code string that will reduce response count.
        A colon is appended to the the filter text to ensure it matches on a code.
    :return: a dictionary of codes and descriptions that match the filter text.

    """
    filter_text_append = f"?text={filter_text}:" if filter_text is not None else ""
    filter_text_append = filter_text_append.replace(':', '%3A', 2)

    url = f"https://www.waterqualitydata.us/Codes/{code_type}code{filter_text_append}"
    content = CACHE.cache_or_fetch(DURATION, url)

    codes = {}
    # TODO what if content is empty or None
    if not content:
        return codes

    xml_data = ElementTree.fromstring(content)
    xml_codes = xml_data.findall("./Code")
    for xml_code in xml_codes:
        code = xml_code.attrib["value"]
        name = xml_code.attrib["desc"]
        codes[code] = name

    return codes


import logging
from django.test import RequestFactory, TestCase
from .codes import Codes

# configure the logger because settings might not be running during tests.
logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.DEBUG)


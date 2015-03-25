import os
import uuid

from unittest2 import TestCase
from yoconfig import configure
from yoconfigurator.base import read_config


class BaseTestCase(TestCase):
    site_id = str(uuid.uuid4())
    country_code = 'US'
    currency = 'USD'
    token = 'token'
    time_zone = 'GMT Standard Time'
    user_name = 'yola test user'
    user_email = 'ekoval@lohika.test.ua'
    password = 'password'
    user_token = 'user_token'
    url = 'http://www.test.site.com'

    @classmethod
    def setUpClass(cls):
        cls.config = read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        configure(sitewit=cls.config.common.sitewit)

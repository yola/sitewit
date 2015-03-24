import os
import uuid

from unittest2 import TestCase
from yoconfig import configure
from yoconfigurator.base import read_config


class BaseTestCase(TestCase):
    site_id = uuid.uuid4()
    country_code = 'US'
    currency = 'USD'
    token = 'token'
    url = 'http://test.test.test'
    time_zone = 'Pacific Standard Time'
    user_name = 'yola test user'
    user_email = 'ekoval@lohika.test.ua'
    password = 'password'
    user_token = 'user_token'

    @classmethod
    def setUpClass(cls):
        cls.config = read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        configure(sitewit=cls.config.common.sitewit)

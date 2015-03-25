from string import ascii_letters
import os
import random
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

    @classmethod
    def setUpClass(cls):
        cls.config = read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        configure(sitewit=cls.config.common.sitewit)

    def generate_url(self):
        # We have to generate new URL each time, because if we try to Create
        # Account using URL of an existent account, no error will be raised,
        # and existent account data will be returned.
        letters_list = list(ascii_letters)
        random.shuffle(letters_list)
        shuffled = ''.join(letters_list)
        return 'http://%s.%s.%s' % (
            shuffled[0:5], shuffled[6:12], shuffled[13:18])

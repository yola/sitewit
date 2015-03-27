import base64
import os
import uuid

from demands import HTTPServiceError
from mock import Mock
from unittest2 import TestCase, skip
from yoconfig import configure
from yoconfigurator.base import read_config

from sitewit.services import SitewitService


class BaseTestCase(TestCase):
    account_id = 9999
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

    response_brief = {
        'accountNumber': account_id,
        'url': url,
        'country': country_code,
        'timeZone': time_zone,
        'currency': currency,
        'clientId': site_id,
        'jsCode': 'jscode',
        'token': token,
        'status': 'Active'
    }

    @classmethod
    def setUpClass(cls):
        cls.config = read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        configure(sitewit=cls.config.common.sitewit)

    def assertAccountIsValid(self, account, check_user_info=False):
        self.assertEqual(account.id, self.account_id)
        self.assertEqual(account.url, self.url)
        self.assertEqual(account.site_id, self.site_id)
        self.assertEqual(account.currency, self.currency)
        self.assertEqual(account.country_code, self.country_code)
        self.assertEqual(account.status, 'Active')
        self.assertEqual(account.token, self.token)

        if check_user_info:
            self.assertEqual(account.user.name, self.user_name)
            self.assertEqual(account.user.email, self.user_email)
            self.assertEqual(account.user.token, self.user_token)

    def assertDemandsIsCalled(self, demands_mock, data=None,
                              account_token=None):
        partner_id = self.config.common.sitewit['affiliate_id']
        partner_token = self.config.common.sitewit['affiliate_token']

        auth_info = '%s:%s' % (partner_id, partner_token)
        if account_token is not None:
            auth_info = '%s:%s' % (auth_info, account_token)

        auth_header = base64.b64encode(auth_info)
        headers = {'PartnerAuth': auth_header}

        if data is not None:
            demands_mock.assert_called_once_with(
                '/api/account/', data, headers=headers)
        else:
            demands_mock.assert_called_once_with(
                '/api/account/', headers=headers)


    def _mock_response(self, requests_mock, response):
        response_mock = Mock()
        response_mock.json = Mock(return_value=response)
        requests_mock.return_value = response_mock


class BaseObjectDoesntExistTestCase(BaseTestCase):
    operation = None

    def setUp(self):
        self.service = SitewitService()

    def test_exception_is_raised(self):
        if self.operation is None:
            return skip("BaseTest tests skipped")

        with self.assertRaises(HTTPServiceError) as exc:
            self.operation()

        expected_error_details = {
            u'Message': u'Malformed SubPartner Identifier'}

        self.assertEqual(exc.exception.response.status_code, 401)
        self.assertEqual(exc.exception.details, expected_error_details)

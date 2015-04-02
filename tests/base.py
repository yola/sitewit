import base64
import os
import uuid

from demands import HTTPServiceError
from mock import Mock
from unittest2 import TestCase
from yoconfig import configure
from yoconfigurator.base import read_config


class SitewitTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        configure(sitewit=cls.config.common.sitewit)

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

    def assertHTTPErrorIsRaised(self, method, params, expected_code,
                                expected_details=None):
        with self.assertRaises(HTTPServiceError) as exc:
            method(*params)

        self.assertEqual(exc.exception.response.status_code, expected_code)
        if expected_details is not None:
            self.assertEqual(exc.exception.details, expected_details)

    @property
    def random_token(self):
        return base64.b64encode(str(uuid.uuid4()))

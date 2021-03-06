import base64
import os
import uuid
from unittest import TestCase

from demands import HTTPServiceError
from mock import Mock
from yoconfig import configure
from yoconfigurator.base import read_config

from sitewit.services import SitewitService


def dict_contains_dict(d1, d2):
    for (key, value) in d2.items():
        if key not in d1:
            return False
        if isinstance(value, dict):
            return dict_contains_dict(d1[key], value)
        if d1[key] != value:
            return False

    return True


class SitewitTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        configure(sitewit=cls.config.common.sitewit)
        cls.service = SitewitService()

    def assertDemandsIsCalled(self, demands_mock, data=None,
                              account_token=None, url='/api/account/',
                              remote_subpartner_id=None):
        partner_id = self.config.common.sitewit['affiliate_id']
        partner_token = self.config.common.sitewit['affiliate_token']

        auth_info = '%s:%s' % (partner_id, partner_token)

        if account_token is not None:
            auth_info = '%s:%s' % (auth_info, account_token)

        auth_header = base64.b64encode(auth_info.encode('utf8'))
        headers = {'PartnerAuth': auth_header}
        if remote_subpartner_id is not None:
            headers['RemoteSubPartnerId'] = base64.b64encode(
                remote_subpartner_id.encode('utf8'))

        if data is not None:
            demands_mock.assert_called_once_with(
                url, json=data, headers=headers)
        else:
            demands_mock.assert_called_once_with(url, headers=headers)

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

    def assertDictContainsDict(self, d1, d2):
        return self.assertTrue(dict_contains_dict(d1, d2))

    @property
    def random_token(self):
        return uuid.uuid4().hex

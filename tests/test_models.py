import base64

from mock import Mock, patch

import sitewit.models
from sitewit.models import Account
from base import BaseTestCase


class TestCreateSitewitAccount(BaseTestCase):
    @patch.object(sitewit.models.SitewitService, 'post')
    def setUp(self, create_account_mock):
        self.response = {
            'accountInfo': {
                'accountNumber': 99999,
                'url': self.url,
                'country': self.country_code,
                'timeZone': self.time_zone,
                'currency': self.currency,
                'clientId': self.site_id,
                'jsCode': 'jscode',
                'token': self.token,
                'status': 'Active'
            },
            'userInfo': {
                'name': self.user_name,
                'email': self.user_email,
                'token': self.user_token,
                'roles': [
                    'Owner',
                    'Admin'
                ]
            }
        }

        self.create_account_mock = create_account_mock
        post_return_mock = Mock()
        post_return_mock.json = Mock(return_value=self.response)
        create_account_mock.return_value = post_return_mock

        self.site = Mock(id=self.site_id)
        self.user = Mock(
            location=self.country_code, currency=self.currency,
            time_zone=self.time_zone)
        self.user.configure_mock(name=self.user_name, email=self.user_email)

        self.result = Account.create(
            self.user, self.site, self.url, user_token=self.user_token)

    def test_demands_post_is_called(self):
        post_data = {
            'url': self.url,
            'clientId': self.site_id,
            'currency': self.currency,
            'countryCode': self.country_code,
            'timeZone': self.time_zone,
            'name': self.user_name,
            'email': self.user_email,
            'businessType': 'SMB',
            'userToken': self.user_token
        }

        partner_id = self.config.common.sitewit['affiliate_id']
        partner_token = self.config.common.sitewit['affiliate_token']
        auth_header = base64.b64encode('%s:%s' % (partner_id, partner_token))
        post_headers = {'PartnerAuth': auth_header}

        self.create_account_mock.assert_called_once_with(
            '/api/account/', post_data, headers=post_headers)

    def test_account_object_is_returned(self):
        account = self.result
        self.assertEqual(account.url, self.url)
        self.assertEqual(account.site_id, self.site_id)
        self.assertEqual(account.currency, self.currency)
        self.assertEqual(account.country_code, self.country_code)
        self.assertEqual(account.user.name, self.user_name)
        self.assertEqual(account.user.email, self.user_email)
        self.assertEqual(account.user.token, self.user_token)
        self.assertEqual(account.status, 'Active')

        self.assertIsNotNone(account.id)
        self.assertIsNotNone(account.token)
        self.assertIsNotNone(account, 'password')

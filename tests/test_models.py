import base64
import os

from mock import Mock, patch
from unittest2 import TestCase
from yoconfig import configure
from yoconfigurator.base import read_config

import sitewit.models
from sitewit.models import Account


config = read_config(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        configure(sitewit=config.common.sitewit)


class TestCreateSitewitAccount(BaseTestCase):
    site_id = 'site_id'
    country_code = 'country'
    currency = 'currency'
    time_zone = 'time_zone'
    token = 'token'
    url = 'url'
    time_zone = 'Pacific Standard Time'
    user_name = 'username'
    user_email = 'ekoval@lohika.com'
    password = 'password'
    usertoken = 'usertoken'

    response = {
      "accountInfo": {
        "accountNumber": 99999,
        "url": url,
        "country": country_code,
        "timeZone": time_zone,
        "currency": currency,
        "clientId": site_id,
        "jsCode": "<script type=\"text/javascript\">\r\nvar loc = ((\"https:\" == document.location.protocol) ? \"https://analytics.\" : \"http://analytics.\");\r\ndocument.write(unescape(\"%3Cscript src='\" + loc + \"sitewit.com/v3/99999/sw.js' type='text/javascript'%3E%3C/script%3E\"));\r\n</script>\r\n",
        "token": token,
        "status": "Active"
      },
      "userInfo": {
        "email": user_email,
        "name": user_name,
        "token": "uuuuuuuuuuUuuuuuuuuu",
        "roles": [
          "Owner",
          "Admin"
        ]
      }
    }

    @patch.object(sitewit.models.SitewitService, 'post')
    def setUp(self, create_account_mock):
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
            self.user, self.site, self.url, self.password)

    def test_demands_post_is_called(self):
        post_data = {
            'url': self.url,
            'clientId': self.site_id,
            'currency': self.currency,
            'countryCode': self.country_code,
            'timeZone': self.time_zone,
            'name': self.user_name,
            'email': self.user_email,
            'password': self.password,
            'businessType': 'SMB',
            }

        partner_id = config.common.sitewit['affiliate_id']
        partner_token = config.common.sitewit['affiliate_token']
        auth_header = base64.b64encode('%s:%s' % (partner_id, partner_token))
        post_headers={'PartnerAuth': auth_header}

        self.create_account_mock.assert_called_once_with('/api/account/',
            post_data, headers=post_headers)

    def test_account_object_is_returned(self):
        account = self.result
        self.assertEqual(account.url, self.url)
        self.assertEqual(account.site_id, self.site_id)
        self.assertEqual(account.currency, self.currency)
        self.assertEqual(account.country_code, self.country_code)
        self.assertEqual(account.time_zone, self.time_zone)
        self.assertEqual(account.user_name, self.user_name)
        self.assertEqual(account.user_email, self.user_email)
        self.assertEqual(account.status, 'Active')

        self.assertIsNotNone(account.id)
        self.assertIsNotNone(account.token)
        self.assertIsNotNone(account, 'password')

from mock import Mock, patch

import sitewit.models
from sitewit.models import Account
from base import BaseTestCase


class TestModelsCreateAccount(BaseTestCase):
    @patch.object(sitewit.models.SitewitService, 'post')
    def setUp(self, post_mock):
        self.post_mock = post_mock

        self.response = {
            'accountInfo': {
                'accountNumber': self.account_id,
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

        self._mock_response(post_mock, self.response)

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

        self.assertDemandsIsCalled(self.post_mock, post_data)

    def test_account_object_is_returned(self):
        account = self.result
        self.assertAccountIsValid(account, check_user_info=True)


class TestModelsGetAccount(BaseTestCase):
    @patch.object(sitewit.models.SitewitService, 'get')
    def setUp(self, get_mock):
        self.get_mock = get_mock
        self._mock_response(get_mock, self.response_brief)

        self.result = Account.get(self.token)

    def test_demands_get_is_called(self):
        self.assertDemandsIsCalled(self.get_mock, account_token=self.token)

    def test_account_object_is_returned(self):
        account = self.result
        self.assertAccountIsValid(account)


class TestModelsUpdateAccount(BaseTestCase):
    @patch.object(sitewit.models.SitewitService, 'put')
    def setUp(self, put_mock):
        self.put_mock = put_mock
        self._mock_response(put_mock, self.response_brief)

        self.site = Mock(id=self.site_id)
        self.user = Mock(
            location=self.country_code, currency=self.currency,
            time_zone=self.time_zone)
        self.user.configure_mock(name=self.user_name, email=self.user_email)

        self.account = Account.update(
            self.token, self.url, self.country_code, self.currency)

    def test_demands_put_is_called(self):
        put_data = {
            'url': self.url,
            'currency': self.currency,
            'countryCode': self.country_code,
            'timeZone': 'GMT Standard Time',
        }

        self.assertDemandsIsCalled(self.put_mock, put_data, self.token)

    def test_account_object_is_returned(self):
        self.assertAccountIsValid(self.account)


class TestModelsDeleteAccount(BaseTestCase):
    @patch.object(sitewit.models.SitewitService, 'delete')
    def setUp(self, delete_mock):
        self.delete_mock = delete_mock
        self._mock_response(delete_mock, self.response_brief)

        self.account = Account.delete(self.token)

    def test_demands_delete_is_called(self):
        self.assertDemandsIsCalled(self.delete_mock, account_token=self.token)

    def test_account_object_is_returned(self):
        self.assertAccountIsValid(self.account)


class TestModelsGenerateAccountSSOToken(BaseTestCase):
    @patch.object(sitewit.models.SitewitService, 'get')
    def setUp(self, get_mock):
        self.get_mock = get_mock
        self._mock_response(get_mock, {'token': 'generated_token'})

        self.generated_token = Account.generate_sso_token(
            self.user_token, self.token)

    def test_demands_get_is_called(self):
        partner_id = self.config.common.sitewit['affiliate_id']
        partner_token = self.config.common.sitewit['affiliate_token']
        auth_header = base64.b64encode('%s:%s:%s' % (
            partner_id, partner_token, self.token))
        headers = {'PartnerAuth': auth_header}

        self.get_mock.assert_called_once_with(
            '/api/sso/token', params={'userToken': self.user_token},
            headers=headers)

    def test_valid_token_is_returned(self):
        self.assertTrue(isinstance(self.generated_token, str))
        self.assertTrue(len(self.generated_token) > 5)

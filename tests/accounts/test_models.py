import uuid

from mock import Mock, patch

import sitewit.models
from sitewit.models import Account
from base import AccountTestCase


class TestModelsCreateAccount(AccountTestCase):
    @patch.object(sitewit.models.SitewitService, 'post')
    def setUp(self, post_mock):
        self.post_mock = post_mock

        self.response = {
            'accountInfo': {
                'accountNumber': self.account_id,
                'url': self.url,
                'countryCode': self.country_code,
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

        self.user = Mock(
            location=self.country_code, currency=self.currency,
            time_zone=self.time_zone, partner_id=self.partner_id,
            is_whitelabel=True, preferences={'wl_email': self.user_email})
        self.user.configure_mock(id=self.user_id, name=self.user_name)

        self.result = Account.create(
            self.user, self.url, site_id=self.site_id,
            mobile_phone=self.mobile_phone,
            user_token=self.user_token
        )

    def test_demands_post_is_called(self):
        post_data = {
            'url': self.url,
            'clientId': self.site_id,
            'currency': self.currency,
            'countryCode': self.country_code,
            'timeZone': self.time_zone,
            'name': self.user_name,
            'email': self.user_email,
            'mobilePhone': self.mobile_phone,
            'businessType': 'SMB',
            'userToken': self.user_token,
        }

        self.assertDemandsIsCalled(
            self.post_mock, post_data, remote_subpartner_id=self.partner_id)

    def test_account_object_is_returned(self):
        account = self.result
        self.assertAccountIsValid(account, check_user_info=True)


class TestModelsGetAccount(AccountTestCase):
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


class TestModelsUpdateAccount(AccountTestCase):
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
            self.token, url=self.url, country_code=self.country_code,
            currency=self.currency
        )

    def test_demands_put_is_called(self):
        put_data = {
            'url': self.url,
            'currency': self.currency,
            'countryCode': self.country_code,
        }

        self.assertDemandsIsCalled(self.put_mock, put_data, self.token)

    def test_account_object_is_returned(self):
        self.assertAccountIsValid(self.account)


class TestModelsDeleteAccount(AccountTestCase):
    @patch.object(sitewit.models.SitewitService, 'delete')
    def setUp(self, delete_mock):
        self.delete_mock = delete_mock
        self._mock_response(delete_mock, self.response_brief)

        self.account = Account.delete(self.token)

    def test_demands_delete_is_called(self):
        self.assertDemandsIsCalled(self.delete_mock, account_token=self.token)

    def test_account_object_is_returned(self):
        self.assertAccountIsValid(self.account)


class TestModelsSetAccountClientId(AccountTestCase):
    @patch.object(sitewit.models.SitewitService, 'put')
    def setUp(self, put_mock):
        self.put_mock = put_mock
        self._mock_response(put_mock, self.response_brief)

        self.site = Mock(id=self.site_id)
        self.new_site_id = uuid.uuid4()
        self.account = Account.set_site_id(
            self.token, str(self.new_site_id))

    def test_demands_put_is_called(self):
        put_data = {
            'clientId': str(self.new_site_id)
        }

        self.assertDemandsIsCalled(
            self.put_mock, put_data, self.token, url='/api/Account/ClientId')

    def test_account_object_is_returned(self):
        self.assertAccountIsValid(self.account)

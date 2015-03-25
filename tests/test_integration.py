import uuid

from demands import HTTPServiceError

from base import BaseTestCase
from sitewit.services import SitewitService


class TestCreateAccount(BaseTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

    def test_account_info_is_returned(self):
        account = self.result['accountInfo']

        self.assertEqual(account['url'], self.url.replace('http://', ''))
        self.assertEqual(account['countryCode'], self.country_code)
        self.assertEqual(account['timeZone'], self.time_zone)
        self.assertEqual(account['currency'], self.currency)
        self.assertEqual(account['status'], 'Active')

    def test_user_info_is_returned(self):
        user = self.result['userInfo']
        self.assertEqual(user['name'], self.user_name)
        self.assertEqual(user['email'], self.user_email)
        self.assertIsNotNone(user['token'])


class TestCreateExistingAccount(BaseTestCase):

    def setUp(self):
        service = SitewitService()
        site_id = uuid.uuid4()

        self.account1 = service.create_account(
            site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

        # Please not that we create account with same site_id, but different
        # fields. This should return existing account with given site_id.
        self.account2 = service.create_account(
            site_id, 'http://another.url', 'another_user',
            'another@email.com', self.currency, self.country_code)

    def test_existing_account_is_returned(self):
        self.assertEqual(self.account1['accountInfo']['accountNumber'],
                         self.account2['accountInfo']['accountNumber'])


class TestCreateAccountBadRequest(BaseTestCase):
    def setUp(self):
        self.service = SitewitService()

    def test_exception_is_raised(self):
        with self.assertRaises(HTTPServiceError) as exc:
            self.service.create_account(
                '', '', self.user_name, self.user_email, self.currency,
                self.country_code)

        expected_error_details = {
            u'ModelState': {
                u'account.url': [u'Missing url parameter']
            },
            u'Message': u'The request is invalid.'
        }

        self.assertEqual(exc.exception.response.status_code, 400)
        self.assertEqual(exc.exception.details, expected_error_details)

from demands import HTTPServiceError

from base import BaseTestCase
from sitewit.services import SitewitService


class TestCreateSitewitAccount(BaseTestCase):

    def setUp(self):
        self.url = self.generate_url()
        service = SitewitService()
        self.result = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

    def test_account_info_is_returned(self):
        account = self.result['accountInfo']

        # TODO: Ask SiteWit why URL is returned without prefix. Until this
        # is fixed, this check will fail.
        # self.assertEqual(account['url'], self.url)
        self.assertEqual(account['countryCode'], self.country_code)
        self.assertEqual(account['timeZone'], self.time_zone)
        self.assertEqual(account['currency'], self.currency)
        self.assertEqual(account['status'], 'Active')

    def test_user_info_is_returned(self):
        user = self.result['userInfo']
        self.assertEqual(user['name'], self.user_name)
        self.assertEqual(user['email'], self.user_email)
        self.assertIsNotNone(user['token'])


class TestCreateSitewitAccountBadRequest(BaseTestCase):
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

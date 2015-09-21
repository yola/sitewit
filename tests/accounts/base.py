from uuid import uuid4

from tests.base import SitewitTestCase


class AccountTestCase(SitewitTestCase):
    account_id = 9999
    site_id = uuid4().hex
    user_id = uuid4().hex
    country_code = 'US'
    currency = 'USD'
    token = 'token'
    time_zone = 'GMT Standard Time'
    user_name = 'yola test user'
    user_email = '{}@yola.yola'.format(user_id)
    password = 'password'
    user_token = 'user_token'
    url = 'http://www.test.site.com'

    response_brief = {
        'accountNumber': account_id,
        'url': url,
        'countryCode': country_code,
        'timeZone': time_zone,
        'currency': currency,
        'clientId': site_id,
        'jsCode': 'jscode',
        'token': token,
        'status': 'Active'
    }

    def assertAccountIsValid(self, account, check_user_info=False):
        self.assertEqual(account.id, self.account_id)
        self.assertEqual(account.url, self.url)
        self.assertEqual(account.site_id, self.site_id)
        self.assertEqual(account.currency, self.currency)
        self.assertEqual(account.country_code, self.country_code)
        self.assertEqual(account.status, 'Active')
        self.assertEqual(account.token, self.token)

        if check_user_info:
            self.assertUserInfoIsValid(account)

    def assertUserInfoIsValid(self, account):
        self.assertEqual(account.user.name, self.user_name)
        self.assertEqual(account.user.email, self.user_email)
        self.assertEqual(account.user.token, self.user_token)

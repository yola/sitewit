import uuid

from base import AccountTestCase
from sitewit.models import Account
from sitewit.services import HTTPServiceError, SitewitService


class FakeUser(object):
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name


class TestCreateAccount(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

    def test_account_info_is_returned(self):
        account = self.result['accountInfo']

        self.assertIsNotNone(account['accountNumber'])
        self.assertIsNotNone(account['token'])

        self.assertEqual(account['url'], self.url)
        self.assertEqual(account['countryCode'], self.country_code)
        self.assertEqual(account['timeZone'], self.time_zone)
        self.assertEqual(account['currency'], self.currency)
        self.assertEqual(account['status'], 'Active')

    def test_user_info_is_returned(self):
        user = self.result['userInfo']
        self.assertEqual(user['name'], self.user_name)
        self.assertEqual(user['email'], self.user_email)
        self.assertIsNotNone(user['token'])


class TestCreateExistingAccount(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        site_id = uuid.uuid4()

        self.account1 = service.create_account(
            site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

        # Please note that we create account with same site_id, but different
        # fields. This should return existing account with given site_id.
        self.account2 = service.create_account(
            site_id, 'http://another.url', 'another_user',
            'another@email.com', self.currency, self.country_code)

    def test_existing_account_is_returned(self):
        self.assertEqual(self.account1['accountInfo']['accountNumber'],
                         self.account2['accountInfo']['accountNumber'])


class TestAccountCreationWithUserTokenPassed(AccountTestCase):
    def setUp(self):
        service = SitewitService()
        site_id = uuid.uuid4()

        response = service.create_account(
            site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

        self.user_token = response['userInfo']['token']

        self.response = service.create_account(
            uuid.uuid4(), 'https://foo.bar', self.user_name,
            '{}@yola.com'.format(uuid.uuid4()),
            self.currency, self.country_code, self.user_token)

    def test_creates_new_account_for_the_given_user(self):
        self.assertIsNotNone(self.user_token)
        self.assertEqual(self.user_token, self.response['userInfo']['token'])


class TestCreateAccountBadRequest(AccountTestCase):
    def test_bad_request_error_is_raised(self):
        with self.assertRaises(HTTPServiceError) as e:
            SitewitService().create_account(
                '', '', self.user_name, self.user_email, self.currency,
                self.country_code)

        self.assertEqual(e.exception.response.status_code, 400)
        self.assertEqual(
            e.exception.details['Message'], 'The request is invalid.')
        self.assertIn('account.url', e.exception.details['ModelState'])


class TestGetAccount(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        self.created_account = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

        self.retrieved_account = service.get_account(
            self.created_account['accountInfo']['token'])

    def test_account_is_returned(self):
        created_account = self.created_account['accountInfo']
        retrieved_account = self.retrieved_account

        for field in ('accountNumber', 'token', 'url', 'countryCode',
                      'timeZone', 'currency', 'status'):
            self.assertEqual(retrieved_account[field], created_account[field])


class TestGetAccountDoesNotExist(AccountTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().get_account, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestUpdateAccount(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        self.created_account = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

        self.updated_account = service.update_account(
            self.created_account['accountInfo']['token'], 'http://url.new',
            'GB', 'GBP')

        self.retrieved_account = service.get_account(
            self.updated_account['token'])

    def test_updated_account_is_returned(self):
        account = self.updated_account

        self.assertEqual(account['url'], 'http://url.new')
        self.assertEqual(account['countryCode'], 'GB')
        self.assertEqual(account['currency'], 'GBP')

    def test_other_fields_are_not_updated(self):
        created_account = self.created_account['accountInfo']

        for field in ('accountNumber', 'token', 'status'):
            self.assertEqual(created_account[field],
                             self.retrieved_account[field])
            self.assertEqual(created_account[field],
                             self.updated_account[field])


class TestUpdateAccountBadRequest(AccountTestCase):
    def setUp(self):
        created_account = self.service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)
        self.token = created_account['accountInfo']['token']

    def test_bad_request_error_is_raised(self):
        expected_error_details = {
            u'ModelState': {
                u'account.url': [u'Invalid Url']
            },
            u'Message': u'The request is invalid.'
        }

        self.assertHTTPErrorIsRaised(
            self.service.update_account, (self.token, 'aa', 'GB', 'GBP'),
            400, expected_error_details)


class TestUpdateAccountDoesNotExist(AccountTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().update_account, (
                self.random_token, 'aa', 'bb', 'cc'),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestDeleteAccount(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        self.created_account = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)['accountInfo']

        self.assertEqual(self.created_account['status'], 'Active')

        self.deleted_account = service.delete_account(
            self.created_account['token'])

        self.retrieved_account = service.get_account(
            self.created_account['token'])

    def test_account_is_marked_as_canceled(self):
        for field in ('accountNumber', 'token', 'url', 'countryCode',
                      'timeZone', 'currency'):
            self.assertEqual(self.retrieved_account[field],
                             self.created_account[field],
                             self.deleted_account[field])

        self.assertEqual(self.retrieved_account['status'], 'Canceled')


class TestDeleteAccountDoesNotExist(AccountTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().delete_account, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestGenerateSSOToken(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        created_account = service.create_account(
            self.site_id, self.url, self.user_name, self.user_email,
            self.currency, self.country_code)

        user_token = created_account['userInfo']['token']
        account_token = created_account['accountInfo']['token']
        self.generated_token = service.generate_sso_token(
            user_token, account_token)

    def test_token_is_returned(self):
        self.assertTrue(isinstance(self.token, str))
        self.assertTrue(len(self.generated_token) > 5)


class TestGenerateSSOTokenBadRequest(AccountTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().generate_sso_token,
            (self.random_token, self.random_token),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class AccountAssociationWithNewUser(AccountTestCase):
    """Account.associate_with_new_user()"""

    @classmethod
    def setUpClass(cls):
        super(AccountAssociationWithNewUser, cls).setUpClass()
        user = FakeUser(cls.user_id, cls.user_name)
        cls.old_account = Account.create(user, cls.site_id, cls.url)

        cls.new_user = FakeUser(uuid.uuid4().hex, 'new name')
        cls.new_account = Account.associate_with_new_user(
            cls.old_account.token, cls.new_user)

    def test_changes_user_token(self):
        self.assertNotEqual(
            self.old_account.user.token, self.new_account.user.token)

    def test_new_user_is_created_with_given_attributes(self):
        self.assertEqual(
            self.new_account.user.email, Account._get_email(self.new_user.id))
        self.assertEqual(self.new_account.user.name, 'new name')

    def test_account_remains_unchanged(self):
        self.assertEqual(self.new_account.token, self.old_account.token)

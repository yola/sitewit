import uuid

from base import AccountTestCase
from sitewit.models import Account
from sitewit.services import HTTPServiceError, SitewitService
from tests.partners.base import PartnerTestCase


class FakeUser(object):
    def __init__(self, user_id, name, partner_id, is_whitelabel=False):
        self.id = user_id
        self.name = name
        self.partner_id = partner_id
        self.is_whitelabel = is_whitelabel


class TestCreateAccount(AccountTestCase):

    def setUp(self):
        self.subpartner_id = uuid.uuid4().hex
        self.result = self.create_account(
            remote_subpartner_id=self.subpartner_id)

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

    def test_subpartner_is_created_dynamically(self):
        partner = self.service.get_partner(
            remote_subpartner_id=self.subpartner_id)
        self.assertEqual(partner['remoteId'], self.subpartner_id)


class TestCreateAccountWithRemoteID(AccountTestCase, PartnerTestCase):
    def setUp(self):
        self.remote_subpartner_id = uuid.uuid4().hex
        self.partner = self.service.create_partner(
            'SubPartner{}'.format(self.remote_subpartner_id), self.address,
            self.settings, remote_id=self.remote_subpartner_id)
        self.result = self.create_account(
            remote_subpartner_id=self.remote_subpartner_id)

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
        site_id = uuid.uuid4().hex
        self.account1 = self.create_account(site_id=site_id)

        # Please note that we create account with same site_id, but different
        # fields. This should return existing account with given site_id.
        self.account2 = self.create_account(
            site_id=site_id, url='http://another.url',
            user_name='another_user', user_email='another@email.com')

    def test_existing_account_is_returned(self):
        self.assertEqual(self.account1['accountInfo']['accountNumber'],
                         self.account2['accountInfo']['accountNumber'])


class TestAccountCreationWithUserTokenPassed(AccountTestCase):
    def setUp(self):
        site_id = uuid.uuid4().hex
        response = self.create_account(site_id=site_id)

        self.user_token = response['userInfo']['token']
        self.response = self.create_account(
            site_id=uuid.uuid4().hex, url='https://foo.bar',
            user_email='{}@yola.com'.format(uuid.uuid4()),
            user_token=self.user_token
        )

    def test_creates_new_account_for_the_given_user(self):
        self.assertIsNotNone(self.user_token)
        self.assertEqual(self.user_token, self.response['userInfo']['token'])


class TestCreateAccountBadRequest(AccountTestCase):
    def test_bad_request_error_is_raised(self):
        with self.assertRaises(HTTPServiceError) as e:
            self.create_account(site_id='', url='')

        self.assertEqual(e.exception.response.status_code, 400)
        self.assertEqual(
            e.exception.details['Message'], 'The request is invalid.')
        self.assertIn('account.url', e.exception.details['ModelState'])


class TestGetAccount(AccountTestCase):

    def setUp(self):
        service = SitewitService()
        self.created_account = self.create_account()

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
        self.created_account = self.create_account()

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
        created_account = self.create_account()
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
        self.created_account = self.create_account()['accountInfo']

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
        created_account = self.create_account()

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
        user = FakeUser(cls.user_id, cls.user_name, cls.partner_id)
        cls.old_account = Account.create(user, cls.site_id, cls.url)

        cls.new_user = FakeUser(uuid.uuid4().hex, 'new name', cls.partner_id)
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


class AccountAssociationWithExistentUser(AccountTestCase):
    """Account.associate_with_existent_user()"""

    @classmethod
    def setUpClass(cls):
        super(AccountAssociationWithExistentUser, cls).setUpClass()
        user1 = FakeUser(cls.user_id, cls.user_name, 'Yola')
        cls.account1 = Account.create(user1, cls.site_id, cls.url)

        user2 = FakeUser(uuid.uuid4().hex, 'new name', 'Yola')
        cls.account2 = Account.create(
            user2, uuid.uuid4().hex, 'http://foo2.com')

        cls.account3 = Account.associate_with_existent_user(
            cls.account1.token, cls.account2.user.token)

    def test_changes_user_token(self):
        self.assertEqual(
            self.account3.user.token, self.account2.user.token)

    def _test_account_remains_unchanged(self):
        self.assertEqual(self.account3.token, self.account1.token)


class GetAccountOwners(AccountTestCase):
    def setUp(self):
        account = self.create_account()
        self.user_token = account['userInfo']['token']
        self.users = SitewitService().get_account_owners(
            account['accountInfo']['token'])

    def test_returns_list_of_account_owners(self):
        self.assertIn(self.user_token, [u['token'] for u in self.users])

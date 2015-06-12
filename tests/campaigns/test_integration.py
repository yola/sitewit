from uuid import uuid4

from tests.base import SitewitTestCase


class BaseCampaignTestCase(SitewitTestCase):

    non_existent_campaign_id = 23232323

    @classmethod
    def setUpClass(cls):
        super(BaseCampaignTestCase, cls).setUpClass()

        cls.account_token = cls.service.create_account(
            uuid4().hex, 'http://www.test.site.com', 'Foo',
            'foo{0}@bar.com'.format(uuid4().hex), 'USD', 'US'
        )['accountInfo']['token']

        cls.campaign_id = cls.service.create_campaign(cls.account_token)['id']


class BaseSubscriptionTestCase(BaseCampaignTestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseSubscriptionTestCase, cls).setUpClass()
        cls.campaign = cls.service.subscribe_to_campaign(
            cls.account_token, cls.campaign_id, 500, 'USD')

    def assert_sub_returned(self, response, campaign_id, budget,
                            is_active=True):
        self.assertEqual(response['id'], campaign_id)
        self.assertEqual(response['subscription']['active'], is_active)
        self.assertEqual(response['subscription']['budget'], budget)


class BaseCancelledSubscriptionTestCase(BaseSubscriptionTestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseCancelledSubscriptionTestCase, cls).setUpClass()
        cls.campaign = cls.sesrvice.cancel_campaign_subscription(
            cls.account_token, cls.campaign_id)


class TestGetCampaign(BaseCampaignTestCase):
    def setUp(self):
        self.result = self.service.get_campaign(
            self.account_token, self.campaign_id)

    def test_campaign_is_returned(self):
        self.assertEqual(self.result['id'], self.campaign_id)
        self.assertTrue(self.result['name'].startswith('Test Campaign'))


class TestGetCampaignNotFound(BaseCampaignTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.get_campaign, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestGetCampaignBadAccountToken(BaseCampaignTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.get_campaign, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestListCampaigns(BaseCampaignTestCase):
    def setUp(self):
        self.result = self.service.list_campaigns(self.account_token)

    def test_campaigns_list_is_returned(self):
        for campaign in self.result:
            self.assertIsNotNone(campaign.get('id'))
            self.assertIsNotNone(campaign.get('name'))
            self.assertIsNotNone(campaign.get('status'))


class TestListCampaignsBadAccountToken(BaseCampaignTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.list_campaigns, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestDeleteCampaign(BaseCampaignTestCase):
    def setUp(self):
        self.result = self.service.delete_campaign(
            self.account_token, self.campaign_id)

    def test_deleted_campaign_is_returned(self):
        self.assertEqual(self.result['status'], 'Deleted')


class TestSubscribeToCampaign(BaseSubscriptionTestCase):
    def test_subscription_is_returned(self):
        self.assertTrue(self.campaign['subscription']['active'])


class TestSubscribeToCampaignNotFound(BaseCampaignTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.subscribe_to_campaign, (
                self.account_token,
                self.non_existent_campaign_id, 500, 'USD'), 404)


class TestSubscribeToCampaignValidationError(BaseCampaignTestCase):
    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.subscribe_to_campaign, (
                self.account_token,
                self.non_existent_campaign_id, 0, 'UAH'), 400)


class TestGetCampaignSubscription(BaseCampaignTestCase):
    def setUp(self):
        self.result = self.service.get_campaign_subscription(
            self.account_token, self.campaign_id)

    def test_campaign_info_is_returned(self):
        self.assertEqual(self.result['id'], self.campaign_id)
        self.assertTrue(self.result['name'].startswith('Test Campaign'))
        self.assertTrue('subscription' in self.result)


class TestGetCampaignSubscriptionNotFound(BaseCampaignTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.get_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestGetCampaignSubscriptionBadAccountToken(BaseCampaignTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.get_campaign_subscription, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestListCampaignSubscriptions(BaseSubscriptionTestCase):
    def setUp(self):
        campaign_id = self.service.create_campaign(self.account_token)['id']
        self.service.subscribe_to_campaign(
            self.account_token, campaign_id, 100, 'USD')

        self.result = self.service.list_campaign_subscriptions(
            self.account_token)

    def test_campaign_subscriptions_are_returned(self):
        self.assertEqual(len(self.result), 2)

        for sub in self.result:
            self.assertTrue(sub['name'].startswith('Test Campaign'))


class TestListCampaignSubscriptionsBadAccountToken(BaseCampaignTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.list_campaign_subscriptions, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestCancelCampaignSubscription(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.cancel_campaign_subscription(
            self.account_token, self.campaign_id)

    def test_campaign_is_cancelled(self):
        self.assertEqual(self.result['status'], 'Cancelled')


class TestCancelCampaignSubscriptionBadAccountToken(BaseCampaignTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.cancel_campaign_subscription, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestCancelCampaignSubscriptionNotFound(BaseCampaignTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.cancel_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestSubscribeToCampaignCurrencyMismatch(BaseSubscriptionTestCase):
    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.subscribe_to_campaign, (
                self.account_token,
                self.campaign_id, 500, 'UAH'), 400)


class SubscribeToCampaignActiveSub(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_upgraded_campaign_is_returned(self):
        self.assert_sub_returned(self.result, self.campaign_id, 500)


class SubscribeToCampaignActiveSubDowngrade(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 100, 'USD')

    def test_downgraded_campaign_is_returned(self):
        self.assert_sub_returned(self.result, self.campaign_id, 100)


class SubscribeToCampaignActiveSubUpgrade(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 600, 'USD')

    def test_upgraded_campaign_is_returned(self):
        self.assert_sub_returned(self.result, self.campaign_id, 600)


class SubscribeToCampaignCancelledSub(BaseCancelledSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_resumes_subscription(self):
        self.assert_sub_returned(self.result, self.campaign_id, 500)


class SubscribeToCampaignCancelledSubUpgrade(
        BaseCancelledSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 1000, 'USD')

    def test_upgrades_subscription(self):
        self.assert_sub_returned(self.result, self.campaign_id, 1000)


class SubscribeToCampaignCancelledSubDowngrade(
        BaseCancelledSubscriptionTestCase):
    def setUp(self):
        self.result = self.service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 100, 'USD')

    def test_downgrades_subscription(self):
        self.assert_sub_returned(self.result, self.campaign_id, 100)

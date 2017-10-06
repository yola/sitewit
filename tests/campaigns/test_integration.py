from datetime import datetime, timedelta
from uuid import uuid4

from dateutil.parser import parse

from sitewit.constants import BillingTypes, CampaignServiceTypes, CampaignTypes
from sitewit.models import Subscription
from tests.base import SitewitTestCase


class BaseCampaignTestCase(SitewitTestCase):

    campaign_type = CampaignTypes.SEARCH
    non_existent_campaign_id = 23232323

    @classmethod
    def setUpClass(cls):
        super(BaseCampaignTestCase, cls).setUpClass()

        cls.account_token = cls.service.create_account(
            'http://www.test.site.com', 'Foo',
            'foo{0}@bar.com'.format(uuid4().hex), 'USD', 'US'
        )['accountInfo']['token']

        cls.subscribe_method = cls.subscribe_method()
        cls.unsubscribe_method = cls.unsubscribe_method()
        cls.campaign_id = cls.create_campaign()

    @classmethod
    def create_campaign(cls):
        return cls.service.create_campaign(
            cls.account_token, campaign_type=cls.campaign_type)['id']

    @classmethod
    def subscribe_method(cls):
        if cls.campaign_type == CampaignTypes.SEARCH:
            return cls.service.subscribe_to_search_campaign

        return cls.service.subscribe_to_display_campaign

    @classmethod
    def unsubscribe_method(cls):
        if cls.campaign_type == CampaignTypes.SEARCH:
            return cls.service.cancel_search_campaign_subscription

        return cls.service.cancel_display_campaign_subscription


class BaseSubscriptionTestCase(BaseCampaignTestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseSubscriptionTestCase, cls).setUpClass()

        cls.campaign = cls.subscribe_method(
            cls.account_token, cls.campaign_id, 500, 'USD')

    def assert_sub_returned(self, response, campaign_id, budget,
                            is_active=True):
        self.assertEqual(response['id'], campaign_id)
        self.assertEqual(response['subscription']['active'], is_active)
        self.assertEqual(response['subscription']['budget'], budget)
        self.assertEqual(
            response['subscription']['billingType'], BillingTypes.TRIGGERED)


class BaseCancelledSubscriptionTestCase(BaseSubscriptionTestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseCancelledSubscriptionTestCase, cls).setUpClass()
        cls.campaign = cls.unsubscribe_method(
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


class TestSubscribeToSearchCampaign(BaseSubscriptionTestCase):
    def test_subscription_is_returned(self):
        self.assertTrue(self.campaign['subscription']['active'])


class TestSubscribeToSearchCampaignNoCampaignSpecified(
        BaseSubscriptionTestCase):
    campaign_id = -1

    def test_subscription_is_returned(self):
        self.assertTrue(self.campaign['subscription']['active'])


class TestSubscribeToEverGreenSearchCampaign(BaseCampaignTestCase):
    def setUp(self):
        self.response = self.service.subscribe_to_search_campaign(
            self.account_token, self.campaign_id, 500, 'USD',
            billing_type=BillingTypes.AUTOMATIC)

    def test_creates_subsription_with_automatic_billing_type(self):
        self.assertEqual(
            self.response['subscription']['billingType'],
            BillingTypes.AUTOMATIC)


class TestSubscribeToEverGreenDisplayCampaign(BaseCampaignTestCase):
    campaign_type = CampaignTypes.DISPLAY

    def setUp(self):
        self.response = self.service.subscribe_to_display_campaign(
            self.account_token, self.campaign_id, 500, 'USD',
            billing_type=BillingTypes.AUTOMATIC)

    def test_creates_subsription_with_automatic_billing_type(self):
        self.assertEqual(
            self.response['subscription']['billingType'],
            BillingTypes.AUTOMATIC)


class TestSubscribeToSearchCampaignWithCustomExpiryDate(BaseCampaignTestCase):
    def setUp(self):
        self.expiry_date = datetime.utcnow().date() + timedelta(31)
        self.response = self.subscribe_method(
            self.account_token, self.campaign_id, 500, 'USD',
            expiry_date=self.expiry_date)

    def test_creates_subscription_with_given_expiry_date(self):
        self.assertEqual(
            parse(self.response['subscription']['nextCharge']).date(),
            self.expiry_date)


class TestSubscribeToDisplayCampaignWithExpiryDate(
        TestSubscribeToSearchCampaignWithCustomExpiryDate):
    campaign_type = CampaignTypes.DISPLAY


class TestSubscribeToDisplayCampaign(TestSubscribeToSearchCampaign):
    campaign_type = CampaignTypes.DISPLAY


class TestSubscribeToDisplayCampaignNoCampaignSpecified(
        BaseSubscriptionTestCase):
    campaign_id = -1

    def test_subscription_is_returned(self):
        self.assertTrue(self.campaign['subscription']['active'])


class TestSubscribeToSearchCampaignNotFound(BaseSubscriptionTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.subscribe_method, (
                self.account_token,
                self.non_existent_campaign_id, 500, 'USD'), 404)


class TestSubscribeToDisplayCampaignNotFound(
        TestSubscribeToSearchCampaignNotFound):
    campaign_type = CampaignTypes.DISPLAY


class TestSubscribeToSearchCampaignValidationError(BaseSubscriptionTestCase):
    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.subscribe_method, (
                self.account_token,
                self.non_existent_campaign_id, 0, 'UAH'), 400
        )


class TestSubscribeToDisplayCampaignValidationError(
        TestSubscribeToSearchCampaignValidationError):
    campaign_type = CampaignTypes.DISPLAY


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


class TestListCampaignSubscriptions(BaseCampaignTestCase):
    def setUp(self):
        campaign_id = self.service.create_campaign(self.account_token)['id']
        self.subscribe_method(self.account_token, campaign_id, 100, 'USD')

        self.result = self.service.list_campaign_subscriptions(
            self.account_token)

    def test_campaign_subscriptions_are_returned(self):
        self.assertEqual(len(self.result), 1)

        for sub in self.result:
            self.assertTrue(sub['name'].startswith('Test Campaign'))


class TestListCampaignSubscriptionsBadAccountToken(BaseCampaignTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.service.list_campaign_subscriptions, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestCancelSearchCampaignSubscription(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.unsubscribe_method(
            self.account_token, self.campaign_id)

    def test_campaign_is_cancelled(self):
        self.assertEqual(self.result['status'], 'Cancelled')


class TestCancelDisplayCampaignSubscription(
        TestCancelSearchCampaignSubscription):
    campaign_type = CampaignTypes.DISPLAY


class TestCancelSearchCampaignSubscriptionBadAccountToken(
        BaseSubscriptionTestCase):
    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.unsubscribe_method, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestCancelDisplayCampaignSubscriptionBadAccountToken(
        TestCancelSearchCampaignSubscriptionBadAccountToken):
    campaign_type = CampaignTypes.DISPLAY


class TestCancelSearchCampaignSubscriptionNotFound(BaseSubscriptionTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.unsubscribe_method, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestRefundSubscriptionTestCase(
        BaseCampaignTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestRefundSubscriptionTestCase, cls).setUpClass()
        cls.result = cls.service.refund_search_campaign_subscription(
            cls.account_token, cls.campaign_id)

    @classmethod
    def create_campaign(cls):
        return cls.subscribe_method(cls.account_token, -1, 500, 'USD')['id']

    def test_refund_request_is_accepted(self):
        self.assertEqual(self.result['campaignInfo']['status'], 'Cancelled')
        self.assertEqual(self.result['refundAmount'], -500.0)


class TestCancelPrePurchasedSubscriptionTestCase(
        BaseCampaignTestCase):

    @classmethod
    def create_campaign(cls):
        # Pre-purchased campaign created "on the fly", when we subscribe
        # to it.
        return cls.subscribe_method(cls.account_token, -1, 500, 'USD')['id']

    def test_subscription_cannot_be_cancelled(self):
        self.assertHTTPErrorIsRaised(
            self.unsubscribe_method, (
                self.account_token, self.campaign_id), 409
        )


class TestCancelDisplayCampaignSubscriptionNotFound(
        TestCancelSearchCampaignSubscriptionNotFound):
    campaign_type = CampaignTypes.DISPLAY


class TestSubscribeToSearchCampaignCurrencyMismatch(BaseSubscriptionTestCase):
    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            self.subscribe_method, (
                self.account_token,
                self.campaign_id, 500, 'UAH'), 400)


class TestSubscribeToDisplayCampaignCurrencyMismatch(
        TestSubscribeToSearchCampaignCurrencyMismatch):
    campaign_type = CampaignTypes.DISPLAY


class SubscribeToSearchCampaignActiveSub(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.subscribe_method(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_upgraded_campaign_is_returned(self):
        self.assert_sub_returned(self.result, self.campaign_id, 500)


class SubscribeToDisplayCampaignActiveSub(
        SubscribeToSearchCampaignActiveSub):
    campaign_type = CampaignTypes.DISPLAY


class SubscribeToSeachCampaignActiveSubDowngrade(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.subscribe_method(
            self.account_token, self.campaign_id, 100, 'USD')

    def test_downgraded_campaign_is_returned(self):
        self.assert_sub_returned(self.result, self.campaign_id, 100)


class SubscribeToDisplayCampaignActiveSubDowngrade(
        SubscribeToSeachCampaignActiveSubDowngrade):
    campaign_type = CampaignTypes.DISPLAY


class SubscribeToSearchCampaignActiveSubUpgrade(BaseSubscriptionTestCase):
    def setUp(self):
        self.result = self.subscribe_method(
            self.account_token, self.campaign_id, 600, 'USD')

    def test_upgraded_campaign_is_returned(self):
        self.assert_sub_returned(self.result, self.campaign_id, 600)


class SubscribeToDisplayCampaignActiveSubUpgrade(
        SubscribeToSearchCampaignActiveSubUpgrade):
    campaign_type = CampaignTypes.DISPLAY


class SubscribeToSearchCampaignCancelledSub(
        BaseCancelledSubscriptionTestCase):
    def setUp(self):
        self.result = self.subscribe_method(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_resumes_subscription(self):
        self.assert_sub_returned(self.result, self.campaign_id, 500)


class SubscribeToDisplayCampaignCancelledSub(
        BaseCancelledSubscriptionTestCase):
    campaign_type = CampaignTypes.DISPLAY


class SubscribeToSearchCampaignCancelledSubUpgrade(
        BaseCancelledSubscriptionTestCase):
    def setUp(self):
        self.result = self.subscribe_method(
            self.account_token, self.campaign_id, 1000, 'USD')

    def test_upgrades_subscription(self):
        self.assert_sub_returned(self.result, self.campaign_id, 1000)


class SubscribeToDisplayCampaignCancelledSubUpgrade(
        BaseCancelledSubscriptionTestCase):
    campaign_type = CampaignTypes.DISPLAY


class SubscribeToSearchCampaignCancelledSubDowngrade(
        BaseCancelledSubscriptionTestCase):
    def setUp(self):
        self.result = self.subscribe_method(
            self.account_token, self.campaign_id, 100, 'USD')

    def test_downgrades_subscription(self):
        self.assert_sub_returned(self.result, self.campaign_id, 100)


class SubscribeToDisplayCampaignCancelledSubDowngrade(
        BaseCancelledSubscriptionTestCase):
    campaign_type = CampaignTypes.DISPLAY


class TestIterSubscriptions(BaseSubscriptionTestCase):
    def setUp(self):
        self.subscription = Subscription.iter_subscriptions().next()

    def test_returns_iterator_over_subscription_objects(self):
        self.assertIsInstance(self.subscription, Subscription)


class TestListSubscriptions(BaseCampaignTestCase):
    def setUp(self):
        self.subscriptions = self.service.list_subscriptions(0, 1)

    def test_limits_returned_result_to_given_limit(self):
        self.assertEqual(len(self.subscriptions), 1)


class TestRequestDIFMCampaignService(BaseCampaignTestCase):
    """
    SiteWitService.request_difm_campaign_service()
    """

    def setUp(self):
        self.response = self.service.request_difm_campaign_service(
            self.account_token, CampaignServiceTypes.DIFM, uuid4().hex)

    def test_returns_id(self):
        self.assertIn('id', self.response)


class TestRefillSearchCampaignSubscription(BaseSubscriptionTestCase):
    """
    SiteWitService.refill_search_campaign_subscription()
    """

    def setUp(self):
        self.response = self.service.refill_search_campaign_subscription(
            self.account_token, self.campaign_id, 510, 500, 'USD',
            datetime.utcnow().date() + timedelta(32))

    def test_refills_subscription_for_given_amount(self):
        self.assertEqual(self.response['charge']['items'][1]['price'], 510)


class TestRefillDisplayCampaignSubscription(BaseSubscriptionTestCase):
    """
    SiteWitService.refill_display_campaign_subscription()
    """

    campaign_type = CampaignTypes.DISPLAY

    def setUp(self):
        self.response = self.service.refill_display_campaign_subscription(
            self.account_token, self.campaign_id, 510, 500, 'USD',
            datetime.utcnow().date() + timedelta(32))

    def test_refills_subscription_for_given_amount(self):
        self.assertEqual(self.response['charge']['items'][1]['price'], 510)

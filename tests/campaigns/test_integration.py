from mock import patch

from base import CampaignTestCase
import sitewit.services
from sitewit.services import SitewitService


class TestGetCampaign(CampaignTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.get_campaign(
            self.account_token, self.campaign_id)

    def test_campaign_is_returned(self):
        self.assertEqual(self.result['id'], self.campaign_id)
        self.assertEqual(self.result['name'], self.campaigns[1]['name'])


class TestGetCampaignNotFound(CampaignTestCase):

    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().get_campaign, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestGetCampaignBadAccountToken(CampaignTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().get_campaign, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestListCampaigns(CampaignTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.list_campaigns(self.account_token)

    def test_campaigns_list_is_returned(self):
        for campaign in self.result:
            self.assertIsNotNone(campaign.get('id'))
            self.assertIsNotNone(campaign.get('name'))
            self.assertIsNotNone(campaign.get('status'))


class TestListCampaignsBadAccountToken(CampaignTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().list_campaigns, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestDeleteCampaign(CampaignTestCase):
    # We test DELETE using mocks, because there is no CREATE endpoint.

    @patch.object(sitewit.services.SitewitService, 'delete')
    def setUp(self, delete_mock):
        self.delete_mock = delete_mock
        self._mock_response(delete_mock, 'result')
        service = SitewitService()
        self.result = service.delete_campaign(
            self.account_token, self.campaign_id)

    def test_requests_is_called(self):
        self.assertDemandsIsCalled(
            self.delete_mock, account_token=self.account_token,
            url='/api/campaign/%s' % (self.campaign_id,))

    def test_subscription_is_returned(self):
        self.assertEqual(self.result, 'result')


class TestSubscribeToCampaign(CampaignTestCase):
    # We test Subscribe Campaign using mocks, because there is no CREATE endpoint.

    @patch.object(sitewit.services.SitewitService, 'post')
    def setUp(self, post_mock):
        self.post_mock = post_mock
        self._mock_response(post_mock, 'result')
        service = SitewitService()
        self.result = service.subscribe_to_campaign(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_requests_is_called(self):
        self.assertDemandsIsCalled(
            self.post_mock, data={'campaignId': self.campaign_id,
                                  'budget': 500,
                                  'currency': 'USD'},
            account_token=self.account_token,
            url='/api/subscription/campaign/')

    def test_subscription_is_returned(self):
        self.assertEqual(self.result, 'result')


class TestSubscribeToCampaignNotFound(CampaignTestCase):
    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().subscribe_to_campaign, (
                self.account_token,
                self.non_existent_campaign_id, 500, 'USD'), 404)


class TestSubscribeToCampaignValidationError(CampaignTestCase):
    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().subscribe_to_campaign, (
                self.account_token,
                self.non_existent_campaign_id, 0, 'UAH'), 400)


class TestGetCampaignSubscription(CampaignTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.get_campaign_subscription(
            self.account_token, self.campaign_id)

    def test_campaign_info_is_returned(self):
        self.assertEqual(self.result['id'], self.campaign_id)
        self.assertEqual(self.result['name'], 'test dont touch')
        self.assertTrue('subscription' in self.result)


class TestGetCampaignSubscriptionNotFound(CampaignTestCase):

    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().get_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestGetCampaignSubscriptionBadAccountToken(CampaignTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().get_campaign_subscription, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestListCampaignSubscriptions(CampaignTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.list_campaign_subscriptions(self.account_token)

    def test_campaigns_are_returned(self):
        self.assertEqual(len(self.result), len(self.campaigns))

        returned_campaigns = sorted(self.result)
        campaigns = sorted(self.campaigns)

        for i in range(len(returned_campaigns)):
            campaign = returned_campaigns[i]
            self.assertEqual(campaign['id'], campaigns[i]['id'])
            self.assertEqual(campaign['name'], campaigns[i]['name'])
            self.assertTrue('subscription' in campaign)


class TestListCampaignSubscriptionsBadAccountToken(CampaignTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().list_campaign_subscriptions, (self.random_token,),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestRenewCampaignSubscription(CampaignTestCase):

    def setUp(self):
        service = SitewitService()

        # To test "Subscribe" we have to make sure we're not already
        # subscribed.
        subscription = service.get_campaign_subscription(
            self.account_token, self.campaign_id)

        if subscription['status'] != 'Cancelled':
            campaign = service.cancel_campaign_subscription(
                self.account_token, self.campaign_id)
            self.assertEqual(campaign['status'], 'Cancelled')

        self.result = service.renew_campaign_subscription(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_campaign_is_returned(self):
        self.assertEqual(self.result['status'], 'Active')


class TestRenewActiveCampaignSubscription(CampaignTestCase):

    def setUp(self):
        service = SitewitService()

        # To test "Subscribe" we have to make sure we're not already
        # subscribed.
        subscription = service.get_campaign_subscription(
            self.account_token, self.campaign_id)

        if subscription['status'] != 'Cancelled':
            campaign = service.cancel_campaign_subscription(
                self.account_token, self.campaign_id)
            self.assertEqual(campaign['status'], 'Cancelled')

        self.result = service.renew_campaign_subscription(
            self.account_token, self.campaign_id, 500, 'USD')

    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().renew_campaign_subscription, (
                self.account_token,
                self.campaign_id, 500, 'USD'), 400)


class TestRenewCampaignSubscriptionBadAccountToken(CampaignTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().renew_campaign_subscription, (
                self.random_token, self.campaign_id, 500, 'USD'),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestRenewCampaignSubscriptionNotFound(CampaignTestCase):

    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().renew_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id,
                500, 'USD'), 404)


class TestCancelCampaignSubscription(CampaignTestCase):

    def setUp(self):
        service = SitewitService()

        # To test "Cancel" we have to make sure subscription is active.
        subscription = service.get_campaign_subscription(
            self.account_token, self.campaign_id)

        if subscription['status'] != 'Active':
            campaign = service.renew_campaign_subscription(
                self.account_token, self.campaign_id, 500, 'USD')
            self.assertEqual(campaign['status'], 'Active')

        self.result = service.cancel_campaign_subscription(
            self.account_token, self.campaign_id)

    def test_campaign_is_cancelled(self):
        self.assertEqual(self.result['status'], 'Cancelled')


class TestCancelCampaignSubscriptionBadAccountToken(CampaignTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().cancel_campaign_subscription, (
                self.random_token, self.campaign_id),
            401, {u'Message': u'Invalid SubPartner Identifier'})


class TestCancelCampaignSubscriptionNotFound(CampaignTestCase):

    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().cancel_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id), 404)


class TestUpgradeCampaignSubscription(CampaignTestCase):

    def setUp(self):
        service = SitewitService()

        # First we have to make sure subscription is active.
        subscription = service.get_campaign_subscription(
            self.account_token, self.campaign_id)

        self.budget = subscription['subscription']['budget']
        currency = subscription['subscription']['currency']

        if subscription['status'] != 'Active':
            campaign = service.renew_campaign_subscription(
                self.account_token, self.campaign_id, self.budget, currency)

        self.result = service.upgrade_campaign_subscription(
            self.account_token, self.campaign_id, self.budget+10, currency)

    def test_upgraded_campaign_is_returned(self):
        self.assertEqual(self.result['id'], self.campaign_id)
        self.assertEqual(
            self.result['subscription']['budget'], self.budget+10)


class TestUpgradeSubscriptionValidationFailed(CampaignTestCase):

    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().upgrade_campaign_subscription, (
                self.account_token,
                self.campaign_id, 500, 'UAH'), 400)


class TestUpgradeSubscriptionNotFound(CampaignTestCase):

    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().upgrade_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id,
                500, 'USD'), 404)


class TestDowngradeCampaignSubscription(CampaignTestCase):

    def setUp(self):
        service = SitewitService()

        # First we have to make sure subscription is active.
        subscription = service.get_campaign_subscription(
            self.account_token, self.campaign_id)

        self.budget = subscription['subscription']['budget']
        currency = subscription['subscription']['currency']

        if subscription['status'] != 'Active':
            campaign = service.renew_campaign_subscription(
                self.account_token, self.campaign_id, self.budget, currency)

        self.result = service.downgrade_campaign_subscription(
            self.account_token, self.campaign_id, self.budget-10, currency)

    def test_downgraded_campaign_is_returned(self):
        self.assertEqual(self.result['id'], self.campaign_id)
        self.assertEqual(
            self.result['subscription']['budget'], self.budget-10)


class TestDowngradeSubscriptionValidationFailed(CampaignTestCase):

    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().downgrade_campaign_subscription, (
                self.account_token,
                self.campaign_id, 500, 'UAH'), 400)


class TestDowngradeSubscriptionNotFound(CampaignTestCase):

    def test_error_404_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().downgrade_campaign_subscription, (
                self.account_token, self.non_existent_campaign_id,
                500, 'USD'), 404)

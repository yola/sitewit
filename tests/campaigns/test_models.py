from datetime import date
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from sitewit.models import Subscription


subscription_data = {
    'fee': 19.0,
    'campaignId': 23916,
    'nextCharge': '2015-05-08T11:32:03',
    'budget': 200.0,
    'currency': 'EUR',
    'active': True,
    'type': 'SearchCampaign'
}


class SubscriptionTestCase(TestCase):
    site_id = uuid4().hex
    expected_site_id = site_id

    def setUp(self):
        self.subscription = Subscription(
            self.site_id, 'http://example.com', subscription_data)

    def test_subscription_attributes_are_populated_on_initialization(self):
        self.assertEqual(self.subscription.url, 'http://example.com')
        self.assertEqual(self.subscription.site_id, self.expected_site_id)
        self.assertEqual(self.subscription.campaign_id, '23916')
        self.assertEqual(self.subscription.currency, 'EUR')
        self.assertEqual(self.subscription.price, Decimal('19'))
        self.assertEqual(self.subscription.ad_spend, Decimal('200'))
        self.assertEqual(self.subscription.expiry_date, date(2015, 5, 8))


class SubscriptionWithEmptySiteIdTestCase(SubscriptionTestCase):
    site_id = ''
    expected_site_id = None

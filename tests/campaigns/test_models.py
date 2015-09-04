from datetime import date
from decimal import Decimal
from unittest import TestCase

from sitewit.models import Subscription


class SubscriptionTestCase(TestCase):
    def setUp(self):
        subscription_data = {
            'fee': 19.0,
            'campaignId': 23916,
            'nextBillDate': '2015-05-08T11:32:03',
            'budget': 200.0,
            'currency': 'EUR',
            'active': True,
            'type': 'SearchCampaign'
        }
        self.subscription = Subscription(
            'site_id', 'http://example.com', subscription_data)

    def test_subscription_attributes_are_populated_on_initialization(self):
        self.assertEqual(self.subscription.url, 'http://example.com')
        self.assertEqual(self.subscription.site_id, 'site_id')
        self.assertEqual(self.subscription.campaign_id, '23916')
        self.assertEqual(self.subscription.currency, 'EUR')
        self.assertEqual(self.subscription.price, Decimal('19'))
        self.assertEqual(self.subscription.ad_spend, Decimal('200'))
        self.assertEqual(self.subscription.billing_date, date(2015, 5, 8))

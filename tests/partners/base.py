import uuid

from tests.base import SitewitTestCase


class PartnerTestCase(SitewitTestCase):

    address = {
        'street1': '123 Baxter Ct.',
        'street2': 'Apt. 100',
        'city': 'Coolsville',
        'stateProv': 'FL',
        'countryCode': 'US',
        'postalCode': '55555-5555'
    }

    settings = {
        'headerColor': 'cccccc',
        'headerTextColor': '000000',
        'headerLogoUrl': 'https://www.partner.com/resources/sw-wl-logo.png',
        'supportPhone': '800-555-0001',
        'supportEmail': 'support@partner.com',
        'supportUrl': 'https://support.partner.com',
        'mobileAppPrimaryColor': 'cccccc',
        'mobileAppSecondaryColor': '222222',
        'mobileAppLogoUrl': 'https://www.partner.com/resources/sw.png',
        'features': [
            'SEM',
            'Connect',
            'Analytics'
        ]
    }

    partner_data = {
        'name': uuid.uuid4(),
        'address': address,
        'whiteLabelSettings': settings
    }

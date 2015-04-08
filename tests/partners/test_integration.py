import copy
import uuid

from base import PartnerTestCase
from sitewit.services import SitewitService


def deep_sort(d):
    """Sort all lists inside given dict, at all levels."""
    dict_copy = copy.deepcopy(d)

    for key, value in d.items():
        if isinstance(value, list):
            dict_copy[key] = sorted(value)
        elif isinstance(value, dict):
            dict_copy[key] = deep_sort(value)

    return dict_copy


class TestCreatePartner(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        self.partner_name = uuid.uuid4().hex

        self.result = service.create_partner(
            self.partner_name, self.address, self.settings)

        # These fields are taken from config, no need to compare them.
        del self.result['partnerId']
        del self.result['partnerToken']

    def test_campaign_is_returned(self):
        expected_result = dict(self.partner_data)
        expected_result['name'] = self.partner_name
        self.assertEqual(self.result, expected_result)


class TestCreatePartnerDuplicateName(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        self.partner_name = uuid.uuid4().hex

        service.create_partner(
            self.partner_name, self.address, self.settings)

    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().create_partner,
            (self.partner_name, self.address, self.settings), 400)


class TestGetPartner(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        self.create_result = service.create_partner(
            uuid.uuid4().hex, self.address, self.settings)

        self.get_result = service.get_partner(self.create_result['partnerId'])

    def test_partner_is_returned(self):
        self.assertEqual(
            deep_sort(self.create_result), deep_sort(self.get_result))


class TestGetPartnerBadPartnerId(PartnerTestCase):

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().get_partner, (uuid.uuid4().hex,), 401)


class TestUpdatePartnerAddress(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        create_result = service.create_partner(
            uuid.uuid4().hex, self.address, self.settings)

        self.new_address = {
            'street1': '124 Baxter Ct.',
            'street2': 'Apt. 101',
            'city': 'Pleasantwille',
            'stateProv': 'CA',
            'countryCode': 'UA',
            'postalCode': '77777-777'
        }
        self.update_result = service.update_partner_address(
            create_result['partnerId'], self.new_address)

        self.get_result = service.get_partner(
            create_result['partnerId'])['address']

    def test_partner_address_is_returned(self):
        self.assertEqual(self.update_result, self.new_address)

    def test_address_is_updated(self):
        self.assertEqual(self.get_result, self.new_address)


class TestUpdatePartnerAddressValidationFailed(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        self.create_result = service.create_partner(
            uuid.uuid4().hex, self.address, self.settings)

        self.new_address = {
            'street1': '124 Baxter Ct.',
            'street2': 'Apt. 101',
            'city': 'Pleasantwille',
            'stateProv': 'CAAA',
            'countryCode': 'UAAA',
            'postalCode': '77777-777'
        }

    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().update_partner_address, (
                self.create_result['partnerId'], self.new_address), 400)


class TestUpdatePartnerSettings(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        create_result = service.create_partner(
            uuid.uuid4().hex, self.address, self.settings)

        self.new_settings = {
            'headerColor': 'aaaaaa',
            'headerTextColor': '111111',
            'headerLogoUrl': 'https://www.partner.com/sw.png',
            'supportPhone': '800-555-1113',
            'supportEmail': 'somebody@qa.com',
            'supportUrl': 'https://support.new.com',
            'mobileAppPrimaryColor': 'dddddd',
            'mobileAppSecondaryColor': '333333',
            'mobileAppLogoUrl': 'https://www.new.com/new/sw.png',
            'features': [
                'SEM'
            ]
        }

        self.update_result = service.update_partner_settings(
            create_result['partnerId'], self.new_settings)

        self.get_result = service.get_partner(
            create_result['partnerId'])['whiteLabelSettings']

    def test_partner_settings_are_returned(self):
        self.assertEqual(self.update_result, self.new_settings)

    def test_settings_are_updated(self):
        self.assertEqual(self.get_result, self.new_settings)


class TestUpdatePartnerSettingsValidationFailed(PartnerTestCase):

    def setUp(self):
        service = SitewitService()
        self.create_result = service.create_partner(
            uuid.uuid4().hex, self.address, self.settings)

        self.new_settings = {
            'headerColor': 'gggggg',
            'headerTextColor': '111111',
            'headerLogoUrl': 'https://www.partner.com/sw.png',
            'supportPhone': '800-555-1113',
            'supportEmail': 'somebody@qa.com',
            'supportUrl': 'https://support.new.com',
            'mobileAppPrimaryColor': 'dddddd',
            'mobileAppSecondaryColor': '333333',
            'mobileAppLogoUrl': 'https://www.new.com/new/sw.png',
            'features': [
                'SEM', 'nonexistent feature'
            ]
        }

    def test_error_400_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().update_partner_settings, (
                self.create_result['partnerId'], self.new_settings), 400)

from mock import Mock, patch

from base import CampaignTestCase
import sitewit.services
from sitewit.services import SitewitService


class TestGetCampaign(CampaignTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.get_campaign(
            self.account_token, self.campaign_id)

    def test_campaign_is_returned(self):
        self.assertEqual(self.result, self.campaigns[1])


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
            401, {u'Message': u'Malformed SubPartner Identifier'})


class TestListCampaigns(CampaignTestCase):

    def setUp(self):
        service = SitewitService()
        self.result = service.list_campaigns(self.account_token)

    def test_campaigns_list_is_returned(self):
        self.assertEqual(sorted(self.result), sorted(self.campaigns))


class TestListCampaignsBadAccountToken(CampaignTestCase):

    def setUp(self):
        service = SitewitService()

    def test_error_401_is_raised(self):
        self.assertHTTPErrorIsRaised(
            SitewitService().list_campaigns, (self.random_token,),
            401, {u'Message': u'Malformed SubPartner Identifier'})


class TestDeleteCampaign(CampaignTestCase):
    # We test DELETE using mocks, because there is no CREATE endpoint.

    @patch.object(sitewit.services.SitewitService, 'delete')
    def setUp(self, delete_mock):
        self.delete_mock = delete_mock
        self._mock_response(delete_mock, '')
        service = SitewitService()
        self.result = service.delete_campaign(
            self.account_token, self.campaign_id)

    def test_campaign_is_deleted(self):
        self.assertEqual(self.result, '')

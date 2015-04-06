from tests.base import SitewitTestCase


class CampaignTestCase(SitewitTestCase):
    # We have to hardcode these values for integration testing, because SiteWit
    # doesn't have Create Campaign API endpoint. Campaigns are created via UI.
    account_token = '0sj0to2h1so78a6w'
    campaign_id = 23895

    non_existent_campaign_id = 23232323

    campaigns = [
                    {'id': 23900,
                     'name': 'test site stuff'},
                    {'id': 23895,
                     'name': 'test dont touch'}]

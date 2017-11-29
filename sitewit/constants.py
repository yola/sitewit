class CampaignServiceTypes(object):
    QUICKSTART = 'quickstart'


class BillingTypes(object):
    AUTOMATIC = 'Automatic'
    TRIGGERED = 'Triggered'


class CampaignTypes(object):
    DISPLAY = 'display'
    SEARCH = 'search'


CAMPAIGN_SERVICES = {
    CampaignServiceTypes.QUICKSTART: 'QuickStart Campaign'
}

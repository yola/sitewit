import base64

from demands import HTTPServiceClient
from yoconfig import get_config


class SitewitService(HTTPServiceClient):
    """Client for SiteWit's API.

    Example::

        sitewitservice = SitewitService()
        response = sitewitservice.get_account(account_token).

    """
    # We support only GMT for now, so don't want to expose this param at
    # Models level. Just use it everywhere.
    DEFAULT_TIME_ZONE = 'GMT Standard Time'

    def __init__(self, **kwargs):
        self._config = get_config('sitewit')
        self._partner_id = self._config['affiliate_id']
        self._partner_token = self._config['affiliate_token']
        kwargs['url'] = self._config['url']

        super(SitewitService, self).__init__(**kwargs)

    def _get_auth_header(self, account_token=None):
        auth_raw = '%s:%s' % (self._partner_id, self._partner_token)
        if account_token is not None:
            auth_raw += ':%s' % account_token
        return {'PartnerAuth': base64.b64encode(auth_raw)}

    def create_account(self, site_id, url, user_name, user_email,
                       currency, country_code, user_token=None):
        """Create new SiteWit account.

        Args:
            site_id (str): site ID (uuid4).
            url: (str): site URL.
            user_name (str): name of account owner.
            user_email (str): email of account owner.
            currency (str): user's currency.
            country_code (str): user's location.
            user_token (str, optional): user token in case this account is
                owned by existing user.

        Returns:
            JSON of format:
            `https://sandboxpapi.sitewit.com/Help/Api/POST-api-Account`
        """
        data = {
            'url': url,
            'businessType': 'SMB',
            'timeZone': self.DEFAULT_TIME_ZONE,
            'clientId': site_id,
            'name': user_name,
            'email': user_email,
            'currency': currency,
            'countryCode': country_code
        }
        if user_token is not None:
            data['userToken'] = user_token

        return self.post(
            '/api/account/', data, headers=self._get_auth_header()).json()

    def get_account(self, account_token):
        """Get SiteWit account.

        Args:
            account_token (str): account token.

        Returns:
            account json:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Account
        """
        return self.get(
            '/api/account/',
            headers=self._get_auth_header(account_token)).json()

    def update_account(self, account_token, url, country_code, currency):
        """Update SiteWit account.

        Args:
            account_token (str): account token.

        Returns:
            account json:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Account
        """
        data = {
            'url': url,
            'countryCode': country_code,
            'currency': currency,
            'timeZone': self.DEFAULT_TIME_ZONE
        }

        return self.put(
            '/api/account/', data,
            headers=self._get_auth_header(account_token)).json()

    def delete_account(self, account_token):
        """Delete SiteWit account.

        Args:
            account_token (str): account token.

        Returns:
            account json:
            https://sandboxpapi.sitewit.com/Help/Api/DELETE-api-Account
        """
        return self.delete(
            '/api/account/',
            headers=self._get_auth_header(account_token)).json()

    def generate_sso_token(self, user_token, account_token):
        """Generate temporary SSO token for given user.

        Args:
            user_token (str): user's token to generate SSO token.
            account_token (str): account token.

        Returns:
            SSO token
        """
        result = self.get(
            '/api/sso/token', params={'userToken': user_token},
            headers=self._get_auth_header(account_token)).json()

        return result['token']

    def get_campaign(self, account_token, campaign_id):
        """Get Campaign info by campaign ID

        Args:
            campaign_id (str): id of campaign.

        Returns:
            dict of format:   {'id': 1, 'name': 'test', 'status': 'Active'}
        """
        return self.get(
            '/api/campaign/%s' % (campaign_id,),
            headers=self._get_auth_header(account_token)).json()

    def list_campaigns(self, account_token):
        """List campaigns available for given account.

        Args:
            account_token (str): account token.

        Returns:
            List of dicts:
            [{'id': 1, 'name': 'test', 'status': 'Active'},...]
        """
        return self.get(
            '/api/campaign/',
            headers=self._get_auth_header(account_token)).json()

    def delete_campaign(self, account_token, campaign_id):
        """Delete Campaign by campaign ID

        Args:
            campaign_id (str): id of campaign.

        Returns:
            dict of format:   {'id': 1, 'name': 'test', 'status': 'Active'}
        """
        return self.delete(
            '/api/campaign/%s' % (campaign_id,),
            headers=self._get_auth_header(account_token)).json()

    def subscribe_to_campaign(self, account_token, campaign_id, budget,
                              currency):
        """Subscribe to campaign.

        Create subscription to a given Campaign for given Account.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            budget (decimal): Desired monthly spend budget (50>=budget<=5000).
            currency (str): https://sandboxpapi.sitewit.com/Help/ResourceModel
                            ?modelName=BudgetCurrency

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            POST-api-subscription-campaign
        """
        data = {'campaignId': campaign_id,
                'budget': budget,
                'currency': currency}

        return self.post('/api/subscription/campaign/', data,
                         headers=self._get_auth_header(account_token)).json()

    def get_campaign_subscription(self, account_token, campaign_id):
        """Get campaign subscription info.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-campaign-id
        """
        return self.get(
            '/api/subscription/campaign/%s' % (campaign_id,),
            headers=self._get_auth_header(account_token)).json()

    def list_campaign_subscriptions(self, account_token):
        """Get all subscriptions to given campaign for given account.

        Create subscription to a given Campaign for given Account.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
        """
        return self.get(
            '/api/subscription/campaign/',
            headers=self._get_auth_header(account_token)).json()

    def upgrade_campaign_subscription(self, account_token, campaign_id,
                                      new_budget, currency):
        """Upgrade campaign subscription.

        Increase campaign budget.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            new_budget (decimal): new campaign budget.
            currency (decimal): currency for new budget.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-campaign-id
        """
        data = {'campaignId': campaign_id,
                'budget': new_budget,
                'currency': currency}

        return self.put('/api/subscription/campaign/upgrade/', data,
                        headers=self._get_auth_header(account_token)).json()

    def downgrade_campaign_subscription(self, account_token, campaign_id,
                                        new_budget, currency):
        """Upgrade campaign subscription.

        Decrease campaign budget.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            new_budget (decimal): new campaign budget.
            currency (decimal): currency for new budget.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-campaign-id
        """
        data = {'campaignId': campaign_id,
                'budget': new_budget,
                'currency': currency}

        return self.put(
            '/api/subscription/campaign/downgrade/', data,
            headers=self._get_auth_header(account_token)).json()

    def resume_campaign_subscription(self, account_token, campaign_id,
                                     new_budget, currency):
        """Resume campaign subscription.

        Resume campaign subscription. If campaign is active, it is returned
        without any actions.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-campaign-id
        """
        data = {'campaignId': campaign_id,
                'budget': new_budget,
                'currency': currency}

        return self.put(
            'api/subscription/reinstate/campaign/', data,
            headers=self._get_auth_header(account_token)).json()

    def cancel_campaign_subscription(self, account_token, campaign_id,
                                     immediate=True):
        """Cancel campaign subscription.

        Cancel campaign subscription.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            immediate (boolean): cancel immediately or wait till the billing
            period ends.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-campaign-id
        """
        data = {'campaignId': campaign_id,
                'cancelType': 'Immediate' if immediate else 'EndOfCycle'}

        return self.delete(
            'api/subscription/cancel/campaign/search/', data=data,
            headers=self._get_auth_header(account_token)).json()

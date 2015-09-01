import base64
from copy import deepcopy

from demands import HTTPServiceClient
from yoconfig import get_config

import sitewit


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
        config = deepcopy(get_config('sitewit'))
        config['client_name'] = sitewit.__name__
        config['client_version'] = sitewit.__version__
        config['send_as_json'] = True
        config.update(kwargs)

        self._partner_id = config['affiliate_id']
        self._partner_token = config['affiliate_token']

        super(SitewitService, self).__init__(config.pop('api_url'), **config)

    def _get_account_auth_header(self, account_token):
        return self._compose_auth_header((
            self._partner_id, self._partner_token, account_token))

    def _get_partner_auth_header(self, subpartner_id=None):
        auth_list = [self._partner_id, self._partner_token]
        if subpartner_id is not None:
            auth_list.append(subpartner_id)
        return self._compose_auth_header(auth_list)

    def _compose_auth_header(self, elements):
        return {'PartnerAuth': base64.b64encode(':'.join(elements))}

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
            '/api/account/', data,
            headers=self._get_partner_auth_header()).json()

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
            headers=self._get_account_auth_header(account_token)).json()

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
            headers=self._get_account_auth_header(account_token)).json()

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
            headers=self._get_account_auth_header(account_token)).json()

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
            headers=self._get_account_auth_header(account_token)).json()

        return result['token']

    def create_campaign(self, account_token):
        """Create new Campaign (for testing purpose)

        Args:
            account_token (str): account token.

        Returns:
            dict of the format:   {'id': 1, 'name': 'test', 'status': 'Unpaid'}
        """
        return self.post(
            '/api/campaign/',
            headers=self._get_account_auth_header(account_token)
        ).json()

    def get_campaign(self, account_token, campaign_id):
        """Get Campaign info by campaign ID

        Args:
            campaign_id (str): id of campaign.

        Returns:
            dict of format:   {'id': 1, 'name': 'test', 'status': 'Active'}
        """
        return self.get(
            '/api/campaign/%s' % (campaign_id,),
            headers=self._get_account_auth_header(account_token)).json()

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
            headers=self._get_account_auth_header(account_token)).json()

    def delete_campaign(self, account_token, campaign_id):
        """Delete Campaign by campaign ID

        Args:
            campaign_id (str): id of campaign.

        Returns:
            dict of format:   {'id': 1, 'name': 'test', 'status': 'Active'}
        """
        return self.delete(
            '/api/campaign/%s' % (campaign_id,),
            headers=self._get_account_auth_header(account_token)).json()

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

        return self.post(
            '/api/subscription/campaign/', data,
            headers=self._get_account_auth_header(account_token)).json()

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
            headers=self._get_account_auth_header(account_token)).json()

    def list_campaign_subscriptions(self, account_token):
        """Get all subscriptions to given campaign for given account.

        Args:
            account_token (str): account token.
        """
        return self.get(
            '/api/subscription/campaign/',
            headers=self._get_account_auth_header(account_token)).json()

    def list_subscriptions(self, page_number=0, page_size=50):
        """Get all active subscriptions grouped by SiteWit account

        Args:
            page_number (int): current page
            page_size (int): number of accounts per page

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-audit_limit_skip
        """
        return self.get(
            '/api/subscription/audit',
            params={'limit': page_size, 'skip': page_number},
            headers=self._get_partner_auth_header()
        ).json()

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
            headers=self._get_account_auth_header(account_token)).json()

    def create_partner(self, name, address, settings):
        """Create partner.

        Create subpartner for current partner.

        Args:
            name (str): partner name.
            address (dict): partner's address.
                https://sandboxpapi.sitewit.com/Help/ResourceModel?
                modelName=Address%20%28Create%29
            settings (dict): WL settings.
                https://sandboxpapi.sitewit.com/Help/ResourceModel?modelName=
                White%20Label%20Settings%20%28Create%29

        Returns:
            Please see response specification here:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Partner
        """
        data = {'name': name,
                'address': address,
                'whiteLabelSettings': settings}

        return self.post(
            '/api/partner/', data=data,
            headers=self._get_partner_auth_header()).json()

    def get_partner(self, subpartner_id):
        """Get subpartner by subpartner id.

        Get subpartner by subpartner id.

        Args:
            subpartner_id (str): Subpartner ID.

        Returns:
            Please see response specification here:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Partner
        """
        return self.get(
            'api/partner/',
            headers=self._get_partner_auth_header(subpartner_id)).json()

    def update_partner_address(self, subpartner_id, address):
        """Update partner's address.

        Update partner's address.

        Args:
            subpartner_id (str): Subpartner ID.
            address (dict): partner's address.
                See details here:
                https://sandboxpapi.sitewit.com/Help/Api/
                PUT-api-partner-address

        Returns:
            Address specification, see details here:
            https://sandboxpapi.sitewit.com/Help/Api/PUT-api-partner-address
        """
        return self.put(
            'api/partner/address', data=address,
            headers=self._get_partner_auth_header(subpartner_id)).json()

    def update_partner_settings(self, subpartner_id, settings):
        """Update partner's settings.

        Update partner's settings.

        Args:
            subpartner_id (str): Subpartner ID.
            settings (dict): partner's wl settings.
                See details here:
                https://sandboxpapi.sitewit.com/Help/Api/
                PUT-api-partner-whitelabel

        Returns:
            Settings specification, see details here:
            https://sandboxpapi.sitewit.com/Help/Api/PUT-api-partner-whitelabel
        """
        return self.put(
            'api/partner/whitelabel', data=settings,
            headers=self._get_partner_auth_header(subpartner_id),
        ).json()

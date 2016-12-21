import base64
from copy import deepcopy

from demands import HTTPServiceClient, HTTPServiceError  # NOQA
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
        config.update(kwargs)

        self._partner_id = config['affiliate_id']
        self._partner_token = config['affiliate_token']

        super(SitewitService, self).__init__(config.pop('api_url'), **config)

    def _get_account_auth_header(self, account_token):
        return self._compose_auth_header((
            self._partner_id, self._partner_token, account_token))

    def _get_partner_auth_headers(
            self, subpartner_id=None, remote_subpartner_id=None):

        if subpartner_id and remote_subpartner_id:
            raise ValueError(
                'Params subpartner_id and remote_subpartner_id are mutually'
                'exclusive'
            )

        headers = {}
        auth_list = [self._partner_id, self._partner_token]

        if subpartner_id is not None:
            auth_list.append(subpartner_id)

        if remote_subpartner_id is not None:
            headers['RemoteSubPartnerId'] = base64.b64encode(
                remote_subpartner_id)

        headers.update(self._compose_auth_header(auth_list))
        return headers

    def _compose_auth_header(self, elements):
        return {'PartnerAuth': base64.b64encode(':'.join(elements))}

    def create_account(self, site_id, url, user_name, user_email,
                       currency, country_code, user_token=None,
                       remote_subpartner_id=None):
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
            remote_subpartner_id (str, optional): user's partner_id on
                                                  customer side)

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
            'countryCode': country_code,
        }

        if user_token is not None:
            data['userToken'] = user_token

        return self.post(
            '/api/account/', json=data,
            headers=self._get_partner_auth_headers(
                remote_subpartner_id=remote_subpartner_id)).json()

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
            '/api/account/', json=data,
            headers=self._get_account_auth_header(account_token)).json()

    def change_account_owner(self, account_token, user_token=None,
                             user_email=None, user_name=None):
        """Change owner for SiteWit account.

        Associate account with either existing user (if user_token is passed)
        or with a new user (creates it automatically using user_email and
        user_name.

        Args:
            account_token (str): account token.
            user_name (str, optional): name of account owner.
            user_email (str, optinal): email of account owner.
            user_token (str, optional): user token of existing user.

        Returns:
            JSON of format:
            https://sandboxpapi.sitewit.com/Help/Api/PUT-api-Account-Owner
        """
        data = {
            'email': user_email,
            'name': user_name,
            'userToken': user_token
        }
        return self.put(
            '/api/account/owner', json=data,
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

    def get_account_owners(self, account_token):
        """Get all account owners.

        Args:
            account_token (str): account token.

        Returns:
            JSON of format:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-User
        """
        return self.get(
            'api/user', headers=self._get_account_auth_header(account_token)
        ).json()

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

    def create_campaign(self, account_token, campaign_type='search'):
        """Create new Campaign (for testing purpose)

        Args:
            account_token (str): account token.
            campaign_type (str): campaign type ("display"/"search").

        Returns:
            dict of the format:   {'id': 1, 'name': 'test', 'status': 'Unpaid'}
        """
        return self.post(
            '/api/campaign/create', json={'type': campaign_type},
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

    def subscribe_to_search_campaign(self, account_token, campaign_id, budget,
                                     currency):
        """Subscribe to Search campaign.

        Create subscription to a given Search Campaign for given Account.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            budget (decimal): Desired monthly spend budget (50>=budget<=5000).
            currency (str): https://sandboxpapi.sitewit.com/Help/ResourceModel
                            ?modelName=BudgetCurrency

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            POST-api-subscription-campaign-search
        """
        data = {'campaignId': campaign_id,
                'budget': budget,
                'currency': currency}

        return self.post(
            '/api/subscription/campaign/search', json=data,
            headers=self._get_account_auth_header(account_token)).json()

    def subscribe_to_display_campaign(
            self, account_token, campaign_id, budget, currency):
        """Subscribe to Display campaign.

        Create subscription to a given Display Campaign for given Account.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            budget (decimal): Desired monthly spend budget (50>=budget<=5000).
            currency (str): https://sandboxpapi.sitewit.com/Help/ResourceModel
                            ?modelName=BudgetCurrency

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            POST-api-subscription-campaign-display
        """
        data = {'campaignId': campaign_id,
                'budget': budget,
                'currency': currency}

        return self.post(
            '/api/subscription/campaign/display', json=data,
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

    def list_subscriptions(self, offset=0, limit=50):
        """Get active subscriptions for all SiteWit accounts.

        Returned data is grouped by account.

        Args:
            offset (int): The number of accounts to skip
            limit (int): number of accounts returned per call

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            GET-api-subscription-audit_limit_skip
        """
        return self.get(
            '/api/subscription/audit',
            params={'limit': limit, 'skip': offset},
            headers=self._get_partner_auth_headers()
        ).json()

    def cancel_search_campaign_subscription(self, account_token, campaign_id,
                                            immediate=True):
        """Cancel Search campaign subscription.

        Cancel Search campaign subscription.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            immediate (boolean): cancel immediately or wait till the billing
            period ends.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            DELETE-api-subscription-cancel-campaign-search
        """
        data = {'campaignId': campaign_id,
                'cancelType': 'Immediate' if immediate else 'EndOfCycle'}

        return self.delete(
            'api/subscription/cancel/campaign/search/', json=data,
            headers=self._get_account_auth_header(account_token)).json()

    def cancel_display_campaign_subscription(self, account_token, campaign_id,
                                             immediate=True):
        """Cancel Display campaign subscription.

        Cancel Display campaign subscription.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            immediate (boolean): cancel immediately or wait till the billing
            period ends.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            DELETE-api-subscription-cancel-campaign-display
        """
        data = {'campaignId': campaign_id,
                'cancelType': 'Immediate' if immediate else 'EndOfCycle'}

        return self.delete(
            'api/subscription/cancel/campaign/display/', json=data,
            headers=self._get_account_auth_header(account_token)).json()

    def create_partner(self, name, address, settings, remote_id=None):
        """Create partner.

        Create subpartner for current partner.

        Args:
            name (str): partner name.
            address (dict): partner's address.
                https://sandboxpapi.sitewit.com/Help/ResourceModel?
                modelName=Address%20%28Create%29
            settings (dict): WL settings.
                https://sandboxpapi.sitewit.com/Help/ResourceModel?modelName=
                White%20Label%20Settings%20%28Create%29,
            remote_id (str): remote id of subpartner

        Returns:
            Please see response specification here:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Partner
        """
        data = {
            'name': name,
            'address': address,
            'whiteLabelSettings': settings,
            'remoteId': remote_id,
        }

        return self.post(
            '/api/partner/', json=data,
            headers=self._get_partner_auth_headers()).json()

    def get_partner(self, subpartner_id=None, remote_subpartner_id=None):
        """Get subpartner by subpartner id.

        Get subpartner by subpartner id.

        Args:
            subpartner_id (str): Subpartner ID.
            remote_subpartner_id (str): Remote Subpartner ID.

        Returns:
            Please see response specification here:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Partner

        Note:
            Parameters are mutually exclusive.
        """
        return self.get(
            'api/partner/',
            headers=self._get_partner_auth_headers(
                subpartner_id, remote_subpartner_id)).json()

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
            'api/partner/address', json=address,
            headers=self._get_partner_auth_headers(subpartner_id)).json()

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
            'api/partner/whitelabel', json=settings,
            headers=self._get_partner_auth_headers(subpartner_id),
        ).json()

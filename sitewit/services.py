import base64
from copy import deepcopy

from demands import HTTPServiceClient, HTTPServiceError  # NOQA
from yoconfig import get_config

import sitewit
from sitewit.constants import BillingTypes, CAMPAIGN_SERVICES, CampaignTypes


_NEXT_CHARGE_PARAMETER_FORMAT = '%Y-%m-%d 23:59:59'


def _remove_nones(data):
    return {k: v for k, v in data.items() if v is not None}


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

    def create_account(self, url, user_name, user_email,
                       currency, country_code, site_id=None,
                       mobile_phone=None, user_token=None,
                       remote_subpartner_id=None):
        """Create new SiteWit account.

        Args:
            url: (str): site URL.
            user_name (str): name of account owner.
            user_email (str): email of account owner.
            currency (str): user's currency.
            country_code (str): user's location.
            site_id (str, optional): site ID (uuid4).
            mobile_phone (str, optional): account owner's phone.
            user_token (str, optional): user token in case this account is
                owned by existing user.
            remote_subpartner_id (str, optional): user's partner_id on
                                                  customer side)

        Returns:
            JSON of format:
            `https://sandboxpapi.sitewit.com/Help/Api/POST-api-Account`
        """
        data = _remove_nones({
            'url': url,
            'businessType': 'SMB',
            'timeZone': self.DEFAULT_TIME_ZONE,
            'name': user_name,
            'email': user_email,
            'currency': currency,
            'countryCode': country_code,
            'userToken': user_token,
            'clientId': site_id,
            'mobilePhone': mobile_phone,
        })

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

    def update_account(
            self, account_token, url=None, country_code=None, currency=None):
        """Update SiteWit account.

        Args:
            account_token (str): account token.

        Returns:
            account json:
            https://sandboxpapi.sitewit.com/Help/Api/GET-api-Account
        """
        data = _remove_nones({
            'url': url,
            'countryCode': country_code,
            'currency': currency,
        })

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

    def set_account_client_id(self, account_token, client_id):
        return self.put(
            '/api/Account/ClientId', json={'clientId': client_id},
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

    def create_campaign(self, account_token,
                        campaign_type=CampaignTypes.SEARCH):
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
            account_token (str): account token.
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
            account_token (str): account token.
            campaign_id (str): id of campaign.

        Returns:
            dict of format:   {'id': 1, 'name': 'test', 'status': 'Active'}
        """
        return self.delete(
            '/api/campaign/%s' % (campaign_id,),
            headers=self._get_account_auth_header(account_token)).json()

    def subscribe_to_search_campaign(
            self, account_token, campaign_id, budget,
            currency, billing_type=BillingTypes.TRIGGERED, expiry_date=None):
        """Subscribe to Search campaign.

        Create subscription to a given Search Campaign for given Account.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            budget (decimal): Desired monthly spend budget (50>=budget<=5000).
            currency (str): https://sandboxpapi.sitewit.com/Help/ResourceModel
                            ?modelName=BudgetCurrency
            billing_type (str, optional): type of billing, either 'Triggered'
                (default) or 'Automatic'
            expiry_date (date, optional): date when a campaign's
                budget is expected to be entirely spent.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            POST-api-subscription-campaign-search
        """
        return self._subscribe_to_campaign(
            CampaignTypes.SEARCH, account_token, campaign_id, budget,
            currency, billing_type, expiry_date)

    def subscribe_to_display_campaign(
            self, account_token, campaign_id, budget, currency,
            billing_type=BillingTypes.TRIGGERED, expiry_date=None):
        """Subscribe to Display campaign.

        Create subscription to a given Display Campaign for given Account.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to subscribe.
            budget (decimal): Desired monthly spend budget (50>=budget<=5000).
            currency (str): https://sandboxpapi.sitewit.com/Help/ResourceModel
                            ?modelName=BudgetCurrency
            billing_type (str, optional): type of billing, either 'Triggered'
                (default) or 'Automatic'
            expiry_date (date, optional): date when a campaign's
                budget is expected to be entirely spent.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            POST-api-subscription-campaign-display
        """
        return self._subscribe_to_campaign(
            CampaignTypes.DISPLAY, account_token, campaign_id, budget,
            currency, billing_type, expiry_date)

    def _subscribe_to_campaign(
            self, campaign_type, account_token, campaign_id, budget, currency,
            billing_type, expiry_date):
        data = {
            'billingType': billing_type,
            'budget': budget,
            'campaignId': campaign_id,
            'currency': currency,
        }

        if expiry_date is not None:
            data['nextCharge'] = expiry_date.strftime(
                _NEXT_CHARGE_PARAMETER_FORMAT)

        return self.post(
            '/api/subscription/campaign/{}'.format(campaign_type), json=data,
            headers=self._get_account_auth_header(account_token)).json()

    def refill_search_campaign_subscription(
            self, account_token, campaign_id, refill_amount, budget, currency,
            expiry_date=None):
        """Refill Search campaign subscription with a given amount.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to refill.
            refill_amount (int): amount we want to refill with.
            budget (int): desired budget (should be exactly the same as
                specified during subscription creation).
            currency (str): currency (should match the value specified
                during subscription creation).
            expiry_date (date, optional): date when a campaign's
                budget is expected to be entirely spent.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            PUT-api-subscription-refill-campaign-search
        """
        return self._refill_campaign_subscription(
            CampaignTypes.SEARCH, account_token, campaign_id, refill_amount,
            budget, currency, expiry_date)

    def refill_display_campaign_subscription(
            self, account_token, campaign_id, refill_amount, budget, currency,
            expiry_date=None):
        """Refill Display campaign subscription with a given amount.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to refill.
            refill_amount (int): amount we want to refill with.
            budget (int): desired budget (should be exactly the same as
                specified during subscription creation).
            currency (str): currency (should match the value specified
                during subscription creation).
            expiry_date (date, optional): date when a campaign's
                budget is expected to be entirely spent.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            PUT-api-subscription-refill-campaign-display
        """
        return self._refill_campaign_subscription(
            CampaignTypes.DISPLAY, account_token, campaign_id, refill_amount,
            budget, currency, expiry_date)

    def _refill_campaign_subscription(
            self, campaign_type, account_token, campaign_id, refill_amount,
            budget, currency, expiry_date):

        data = {
            'budget': budget,
            'campaignId': campaign_id,
            'chargedSpend': refill_amount,
            'currency': currency,
        }

        if expiry_date is not None:
            data['nextCharge'] = expiry_date.strftime(
                _NEXT_CHARGE_PARAMETER_FORMAT)

        return self.put(
            'api/subscription/refill/campaign/{}'.format(campaign_type),
            json=data,
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
            campaign_id (str): campaign to cancel.
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
            campaign_id (str): campaign to cancel.
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

    def refund_search_campaign_subscription(self, account_token, campaign_id):
        """Cancel search subscription and initiate refund.

        Cancels a pre-purchased search campaign's subscription and issues
        a refund for accrued spend. This will only work for campaigns that
        have not launched.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to cancel/refund.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            DELETE-api-subscription-refund-campaign-search-id
        """
        return self.delete(
            'api/subscription/refund/campaign/search/{}'.format(campaign_id),
            headers=self._get_account_auth_header(account_token)).json()

    def refund_display_campaign_subscription(self, account_token, campaign_id):
        """Cancel display subscription and initiate refund.

        Cancels a pre-purchased display campaign's subscription and issues
        a refund for accrued spend. This will only work for campaigns that
        have not launched.

        Args:
            account_token (str): account token.
            campaign_id (str): campaign to cancel/refund.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            DELETE-api-subscription-refund-campaign-display-id
        """
        return self.delete(
            'api/subscription/refund/campaign/display/{}'.format(campaign_id),
            headers=self._get_account_auth_header(account_token)).json()

    def request_quickstart_campaign_service(
            self, account_token, service_type, reference_id):
        """Create a request for QuickStart campaign service.

        Args:
            account_token (str): account token.
            service_type (str): type of the service to request.
            reference_id (str): identifier of service request.

        Returns:
            Please see response format here:
            https://sandboxpapi.sitewit.com/Help/Api/
            POST-api-service-create-campaign-quickstart
        """
        data = {
            'type': CAMPAIGN_SERVICES[service_type],
            'referenceId': reference_id
        }
        return self.post(
            'api/service/create/campaign/quickstart', json=data,
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

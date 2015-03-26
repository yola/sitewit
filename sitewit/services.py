import base64

from demands import HTTPServiceClient
from yoconfig import get_config


class SitewitService(HTTPServiceClient):
    """
    Client for SiteWit's API.

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
        """ Create new SiteWit account.

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

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

    def get_account(self, account_token):
        """ Get SiteWit account.

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
        """ Update SiteWit account.

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
        """ Delete SiteWit account.

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
        """ Generate temporary SSO token for given user.

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

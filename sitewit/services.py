import base64

from demands import HTTPServiceClient
from yoconfig import get_config


class SitewitService(HTTPServiceClient):
    """
    Client for SiteWit's API::

        sitewitservice = SitewitService()
        response = sitewitservice.get_account(account_token).

    """
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
        """ Create new SiteWit account. """
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
        """ Get SiteWit account by Account Token. """
        return self.get(
            '/api/account/', headers=self._get_auth_header(account_token))

    def delete_account(self, account_token):
        """ Delete SiteWit account by Account Token. """
        return self.delete(
            '/api/account/', headers=self._get_auth_header(account_token))

    def update_account(self, account_token, url, location,
                       currency):
        data = {
            'url': url,
            'timeZone': self.DEFAULT_TIME_ZONE,
            'currency': currency,
            'countryCode': location
        }
        return self.put('/api/account/', data, headers=self._get_auth_header())

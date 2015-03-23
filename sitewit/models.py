import json

from sitewit.services import SitewitService


class Account(object):
    _sitewitservice = None
    DEFAULT_TIME_ZONE = 'Pacific Standard Time'

    def __init__(self, account_json):
        self.id = account_json.get('accountNumber')
        self.token = account_json.get('token')
        self.status = account_json.get('status')
        self.url = account_json.get('url')
        self.business_type = 'SMB'
        self.time_zone = account_json.get('timeZone', self.DEFAULT_TIME_ZONE)
        self.site_id = account_json.get('clientId')
        self.user_email = account_json.get('email')
        self.user_name = account_json.get('name')
        self.password = account_json.get('password')
        self.currency = account_json.get('currency')
        self.country_code = account_json.get('country')

    @classmethod
    def get_service(cls):
        if cls._sitewitservice is None:
            cls._sitewitservice = SitewitService()
        return cls._sitewitservice

    @classmethod
    def create(cls, user, site, url, password):
        """ Create SiteWit account for site.
        user: yousers.models.User instance;
        site: yosites.models.Site instance;

        Returns:
            Instance of Account class.
        """
        data = {
            'url': url,
            'time_zone': cls.DEFAULT_TIME_ZONE,
            'site_id': site.id,
            'user_name': user.name,
            'user_email': user.email,
            'password': password,
            'currency': user.currency,
            'country_code': user.country_code
        }
        result = cls.get_service().create_account(
            site.id, url, user.name, user.email, password,
            cls.DEFAULT_TIME_ZONE, user.currency, user.location)

        account_data = result['accountInfo']
        user_data = result['userInfo']
        account_data.update(user_data)

        return Account(account_data)

    @classmethod
    def get(cls, account_token):
        account_json = self.get_service().get_account(account_token)

    def save(self):
        service = self.get_service().update_account(
            self.token, self.url, self.time_zone, self.currency,
            self.country_code)

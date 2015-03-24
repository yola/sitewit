import json

from sitewit.services import SitewitService


class User(object):
    def __init__(self, name, email, token=None):
        self.name = name
        self.email = email
        self.token = token


class Account(object):
    _sitewitservice = None
    DEFAULT_TIME_ZONE = 'Pacific Standard Time'

    def __init__(self, account_data, user_data=None):
        self.id = account_data.get('accountNumber')
        self.token = account_data.get('token')
        self.status = account_data.get('status')
        self.url = account_data.get('url')
        self.time_zone = account_data.get('timeZone', self.DEFAULT_TIME_ZONE)
        self.site_id = account_data.get('clientId')
        self.password = account_data.get('password')
        self.currency = account_data.get('currency')
        self.country_code = account_data.get('country')

        if user_data is not None:
            self.user = User(user_data['name'], user_data['email'],
                             user_data['token'])

    @classmethod
    def get_service(cls):
        if cls._sitewitservice is None:
            cls._sitewitservice = SitewitService()
        return cls._sitewitservice

    @classmethod
    def create(cls, user, site, url, password, user_token=None):
        """ Create SiteWit account for site.
        user: yousers.models.User instance;
        site: yosites.models.Site instance;

        Returns:
            Instance of Account class.
        """
        result = cls.get_service().create_account(
            site.id, url, user.name, user.email, password,
            cls.DEFAULT_TIME_ZONE, user.currency, user.location,
            user_token=user_token)

        account_data = result['accountInfo']
        user_data = result.get('userInfo')

        return Account(result['accountInfo'], user_data=result['userInfo'])

    @classmethod
    def get(cls, account_token):
        account_data = self.get_service().get_account(account_token)
        return Account(account_data)

    def save(self):
        service = self.get_service().update_account(
            self.token, self.url, self.time_zone, self.currency,
            self.country_code)

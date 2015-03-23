import json

from sitewit.services import SitewitService


class Account(object):
    def __init__(self, account_json):
        self.id = account_json.get('accountNumber')
        self.token = account_json.get('token')
        self.status = account_json['status']
        self.url = account_json['url']
        self.business_type = 'SMB'
        self.time_zone = account_json['timeZone'],
        self.client_id = account_json,get('clientId'),
        self.email = account_json.get('email'),
        self.password = account_json.get('password'),
        self.name = account_info.get('name')
        self.currency = account_info.get('currency')
        self.country_code = account_info.get('countryCode')

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
            'businessType': 'SMB',
            'timeZone': user.location,
            'clientId': site.id,
            'email': user.email,
            'password': password,
            'name': user.name,
            'currency': user.currency,
            'countryCode': user.locale
        }

        account_json = self.get_service().create_account(data)
        return Account(account_json)

    @classmethod
    def get(cls, account_token):
        account_json = self.get_service().get_account(account_token)

    def save(self):
        service = self.get_service().update_account(
            self.token, self.url, self.time_zone, self.currency,
            self.country_code)

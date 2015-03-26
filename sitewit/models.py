from sitewit.services import SitewitService


class User(object):
    def __init__(self, name, email, token):
        self.name = name
        self.email = email
        self.token = token


class Account(object):
    _sitewitservice = None

    def __init__(self, account_data, user_data=None):
        self.id = account_data['accountNumber']
        self.token = account_data['token']
        self.status = account_data['status']
        self.url = account_data['url']
        self.site_id = account_data['clientId']
        self.currency = account_data['currency']
        self.country_code = account_data['country']

        if user_data is not None:
            self.user = User(user_data['name'], user_data['email'],
                             user_data['token'])
        else:
            self.user = None

    @classmethod
    def get_service(cls):
        if cls._sitewitservice is None:
            cls._sitewitservice = SitewitService()
        return cls._sitewitservice

    @classmethod
    def create(cls, user, site, url, user_token=None):
        """ Create SiteWit account for site.

        Args:
            user (yousers.models.User instance): user.
            site (yosites.models.Site instance): site.
            url (str): url of given account.
            user_token (str, optiona): user token. Is specified if the user
                has another accounts.

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        result = cls.get_service().create_account(
            site.id, url, user.name, user.email, user.currency,
            user.location, user_token=user_token)

        return Account(result['accountInfo'], user_data=result['userInfo'])

    @classmethod
    def get(cls, account_token):
        """ Get SiteWit account by account token.

        Args:
            account_token (str): account token.

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        result = cls.get_service().get_account(account_token)

        return Account(result)

    @classmethod
    def update(cls, account_token, url, country_code, currency):
        """ Update SiteWit account with given data.

        Args:
            account_token (str): account token.
            url (str): new URL.
            country_code (str): new country code
                (https://sandboxpapi.sitewit.com/Help/ResourceModel?
                 modelName=CountryCode)
            currency (str): new currency
                (https://sandboxpapi.sitewit.com/Help/ResourceModel?
                 modelName=BudgetCurrency

        Returns:
            Instance of account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        result = cls.get_service().update_account(
            account_token, url, country_code, currency)

        return Account(result)

    @classmethod
    def delete(cls, account_token):
        """ Get SiteWit account by account token.

        Args:
            account_token (str): account token.

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        result = cls.get_service().delete_account(account_token)

        return Account(result)

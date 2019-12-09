from decimal import Decimal
import itertools
from uuid import UUID

from dateutil.parser import parse

from sitewit.services import SitewitService


class User(object):
    def __init__(self, name, email, token):
        self.name = name
        self.email = email
        self.token = token


class SiteWitServiceModel(object):
    _sitewitservice = None

    @classmethod
    def get_service(cls):
        if cls._sitewitservice is None:
            cls._sitewitservice = SitewitService()
        return cls._sitewitservice


class Account(SiteWitServiceModel):
    def __init__(self, account_data, user_data=None):
        self.id = account_data['accountNumber']
        self.token = account_data['token']
        self.status = account_data['status']
        self.url = account_data['url']
        self.site_id = account_data['clientId']
        self.currency = account_data['currency']
        self.country_code = account_data['countryCode']

        if user_data is not None:
            self.user = User(user_data['name'], user_data['email'],
                             user_data['token'])
        else:
            self.user = None

    @classmethod
    def create(
        cls,
        user,
        url,
        site_id=None,
        user_token=None,
        mobile_phone=None,
        user_package=None,
    ):
        """Create SiteWit account for given site_id.

        Args:
            user (yousers.models.User instance): user.
            url (str): url of given account.
            site_id (str, optional): Site's ID, UUID
            user_token (str, optional): user token. Is specified if the user
                has another accounts.
            mobile_phone (str, optional): account owner's phone
            user_package (str, optional): package subscription of account's
                owner

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        email = cls._get_email(user)
        user_id = cls._generate_sw_user_id(user)
        user_name = cls._get_valid_user_name(user)
        subpartner_id = user.partner_id if user.is_whitelabel else None

        result = cls.get_service().create_account(
            url, user_id, user_name, email, 'USD', 'US', site_id=site_id,
            mobile_phone=mobile_phone, user_token=user_token,
            remote_subpartner_id=subpartner_id, user_package=user_package)

        return Account(result['accountInfo'], user_data=result['userInfo'])

    @classmethod
    def get(cls, account_token):
        """Get SiteWit account by account token.

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
    def update(
            cls, account_token, url=None, country_code=None, currency=None):
        """Update SiteWit account with given data.

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
            account_token, url=url, country_code=country_code,
            currency=currency)

        return Account(result)

    @classmethod
    def associate_with_new_user(cls, account_token, user):
        """Associate account token with a new user on SiteWit side.

        Args:
            account_token (str): account token.
            user (yousers.models.User instance): user.

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        email = cls._get_email(user)
        user_name = cls._get_valid_user_name(user)
        response = cls.get_service().change_account_owner(
            account_token, user_email=email, user_name=user_name)

        return Account(response['accountInfo'], user_data=response['userInfo'])

    @classmethod
    def associate_with_existent_user(cls, account_token, user_token):
        """Associate account token with an existent user on SiteWit side.

        Args:
            account_token (str): account token.
            user_token (str): user token.

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        response = cls.get_service().change_account_owner(
            account_token, user_token=user_token)

        return Account(response['accountInfo'], user_data=response['userInfo'])

    @classmethod
    def delete(cls, account_token):
        """Get SiteWit account by account token.

        Args:
            account_token (str): account token.

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        result = cls.get_service().delete_account(account_token)

        return Account(result)

    @classmethod
    def set_site_id(cls, account_token, new_site_id):
        """Set new site_id (clientId) for SiteWit account.

        Args:
            account_token (str): account token.
            new_site_id (str): new site_id (clientId)

        Returns:
            Instance of Account class.

        Raises:
            demands.HTTPServiceError: if any error happened on HTTP level.
        """
        result = cls.get_service().set_account_client_id(
            account_token, new_site_id)

        return Account(result)

    @classmethod
    def _get_valid_user_name(cls, user):
        """Return a user name suitable for passing to SiteWit API.

        Account creation will fail for names that are too short or too long.
        """
        full_name = user.get_full_name()
        if 1 < len(full_name) < 256:
            return full_name

        return 'User'

    @classmethod
    def _get_email(cls, user):
        return user.preferences.get('wl_email', user.email)

    @classmethod
    def _generate_sw_user_id(cls, user):
        return '{}@yola.yola'.format(user.id)


class Subscription(SiteWitServiceModel):
    def __init__(self, site_id, url, data):
        self.site_id = UUID(site_id).hex if site_id else None
        self.url = url
        self.ad_spend = Decimal(data['budget'])
        self.price = Decimal(data['fee'])
        self.campaign_id = str(data['campaignId'])
        self.currency = data['currency']
        self.expiry_date = parse(data['nextCharge']).date()

    @classmethod
    def iter_subscriptions(cls):
        """Iterate over all active subscriptions"""
        service = cls.get_service()
        limit = 100

        for offset in itertools.count(0, limit):
            batch = service.list_subscriptions(offset, limit)

            for account_data in batch:
                url = account_data['url']
                site_id = account_data['clientId']
                for subscription_data in account_data['subscriptions']:
                    yield cls(site_id, url, subscription_data)

            if len(batch) < limit:
                return

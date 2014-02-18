import datetime

from suds.client import Client
from .utils import recursive_asdict


class WSDLService(object):

    API_BASE = 'https://api.sitewit.com'
    SANDBOX_API_BASE = 'https://sandboxapi.sitewit.com'

    def __init__(self, wsdl_path, sandbox=False):
        wsdl_url = self.API_BASE + wsdl_path

        if sandbox:
            wsdl_url = self.SANDBOX_API_BASE + wsdl_path

        self.WSDL_URL = wsdl_url
        self.client = Client(wsdl_url)


class VisitorData(WSDLService):
    WSDL_PATH = '/reporting/visitordata.asmx?WSDL'

    def __init__(self, account_token, user_token, sandbox=False):
        self.account_token = account_token
        self.user_token = user_token
        super(VisitorData, self).__init__(self.WSDL_PATH, sandbox=sandbox)

    def get_overview(self, start_date, end_date):
        self.client.service.GetVisitorDetail(
            UserToken=self.user_token,
            AccountToken=self.account_token,
            StartDate=start_date, EndDate=end_date)


class TrafficData(WSDLService):
    WSDL_PATH = '/reporting/trafficdata.asmx?WSDL'

    def __init__(self, account_token, user_token, sandbox=False):
        self.account_token = account_token
        self.user_token = user_token
        super(TrafficData, self).__init__(self.WSDL_PATH, sandbox=sandbox)

    def get_overview(self, start_date, end_date):
        data = self.client.service.GetOverview(
            UserToken=self.user_token,
            AccountToken=self.account_token,
            StartDate=start_date, EndDate=end_date).Data
        if not data:
            return
        return recursive_asdict(data).get('TrafficType', [])



    def get_perfromance_overview(self):
        raise NotImplemented()

    def get_medium_overview(self):
        raise NotImplemented()

    def get_source_overview(self):
        raise NotImplemented()

    def get_overview_comparison(self):
        raise NotImplemented()

    def get_perfromance_overviewcomparison(self):
        raise NotImplemented()

    def get_medium_overview_comparison(self):
        raise NotImplemented()

    def get_source_overview_comparison(self):
        raise NotImplemented()


class AccountInfo(WSDLService):
    WSDL_PATH = '/account/accountinfo.asmx?WSDL'

    def __init__(self, account_token, user_token, sandbox=False):
        self.account_token = account_token
        self.user_token = user_token
        super(AccountInfo, self).__init__(self.WSDL_PATH, sandbox=sandbox)

    def create_account(self, affiliate_id, affiliate_token, account_url, country, timezone,
                       name, business_type='SMB', email=None, client_id=None):
        return self.client.service.CreateAccount(
            AffiliateId=affiliate_id,
            AffiliateToken=affiliate_token,
            AccountURL=account_url,
            Country=country,
            TimeZone=timezone,
            Name=name,
            BusinessType=business_type,
            Email=email,
            ClientId=client_id)

from .service_data import get_traffic_detail_overview
from sitewit.utils import recursive_asdict

from unittest2 import TestCase
from suds.sudsobject import Factory


def create_suds_type(name='FakeSudsObject', **kwargs):
    return Factory.object(name, kwargs)


class UtilsTestCase(TestCase):
    """utils package"""
    @classmethod
    def setUpClass(cls):
        cls.service_data = get_traffic_detail_overview('20140505', '20140506')
        data = {
            'TrafficOverview': {
                'Data': cls.service_data,
            }
        }
        cls.suds_type = create_suds_type('TrafficOverview', **data)

    def test_recursive_dict_has_all_attributes(self):
        self.assertEquals(
            recursive_asdict(self.suds_type).get('TrafficOverview').get('Data'),
            self.service_data)

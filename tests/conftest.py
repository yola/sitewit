import os
import time

import pytest

collect_ignore = []
if os.environ.get('INTEGRATION_TESTS'):
    @pytest.fixture(scope='function', autouse=True)
    def set_up():
        time.sleep(0.5)
else:
    collect_ignore.extend([
        'accounts/test_integration.py',
        'campaigns/test_integration.py',
        'partners/test_integration.py',
    ])

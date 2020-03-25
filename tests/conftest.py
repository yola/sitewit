import os

collect_ignore = []
if not os.environ.get('INTEGRATION_TESTS'):
    collect_ignore.extend([
        'accounts/test_integration.py',
        'campaigns/test_integration.py',
        'partners/test_integration.py',
    ])

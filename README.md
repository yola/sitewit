sitewit
=======

SiteWit Python client

Implemented api end points:
* reporting/trafficdata/get_overview
* account/acountinfo/create_account

## Testing

Install development requirements:

    build-virtualenv

Generate configuration file:

    configurator --local test qa

Run the tests with:

    nosetests

Integration tests are available, but are not run automatically. To run:

    nosetests --include accounts.test_integration \
      --include campaigns.test_integration --include partners.test_integration


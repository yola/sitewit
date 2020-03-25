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

    pytest

Integration tests are available, but are not run automatically. To run:

    INTEGRATION_TESTS=1 pytest

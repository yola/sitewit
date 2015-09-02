# [Changelog](https://github.com/yola/sitewit/releases)

## 0.3.1

* Add `list_subscriptions` service method (to get all active subscriptions)
* Add `Subscription` model with `iter_subscriptions` classmethod

## 0.3.0

* Add `create_campaign` service method (for testing purpose)
* Remove `upgrade_campaign_subscription`, `downgrade_campaign_subscription`,
  `resume_campaign_subscription` service methods, since now we can
  `subscribe_to_campaign` for upgrade/downgrade/reinstate
* Remove old SOAP-based client

## 0.2.0

* Remove needless params from Resume Subscription method.

## 0.1.0

* Support new JSON API.

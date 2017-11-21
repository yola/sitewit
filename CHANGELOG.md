# [Changelog](https://github.com/yola/sitewit/releases)

## 0.9.0

* Rename `SitewitService.request_difm_campaign_service()` to 
    `SitewitService.request_quickstart_campaign_service()`.
* Rename `CampaignServiceTypes.DIFM` to `CampaignServiceTypes.QUICKSTART`.
* Change `CAMPAIGN_SERVICES` to use new SW name `QuickStart Campaign`. 

## 0.8.3

* Add `SitewitService.request_difm_campaign_service()`.
* Add `CampaignServiceTypes` and `CAMPAIGN_SERVICES` constants.

## 0.8.2

* Allow emtpy clientId in model.Subscription.iter_subscriptions (pre-purchased
  campaign case).

## 0.8.1

* Add `SitewitService.refund_search_campaign_subscription()` and
  `SitewitService.refund_display_campaign_subscription()` methods.

## 0.8.0

* Add `models.Account.set_site_id()` method.
* Add `services.SitewitService.set_site_id()` method.
* Re-order parameters of `models.Account.create()` and
  `services.SitewitService.create()`.
* Make `site_id/client_id` parameter optional for account creation.
* Make all field-related parameters of account update optional.

## 0.7.3

* Add `remote_subpartner_id` parameter to `services.get_partner()` method.
* Fix broken unittest
* Make functional tests more robust

## 0.7.2

* Add optional `remote_id` param to `create_partner` method.
* Add optional `remote_subpartner_id` param to `create_account` method.

## 0.7.1

* Fix `Subscription` initialization in `iter_subscriptions` method

## 0.7.0

* Rename `services.subscribe_to_campaign` method to
  `subscribe_to_search_campaign`
* Add `subscribe_to_display_campaign` method
* Rename `services.cancel_campaign_subscription` method to
  `cancel_search_campaign_subscription`
* Add `cancel_display_campaign_subscription` method

## 0.6.0

* Switch to Demands == 4.0.0

## 0.5.0

* Use new endpoint for subscription creation
* Add `get_account_owners` service method

## 0.4.0

* Add service method to change account owner
* Add 2 model methods to associate account with either new user or existing
  user
* Fix `Account` model initialization
* Change `Account.create` to accept `site_id` instead of Site instance
* Fix `Account.create` to populate requested attributes properly.

## 0.3.2

* Add `billing_date` attribute to `Subscription`
* Convert `campaign_id` to string

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

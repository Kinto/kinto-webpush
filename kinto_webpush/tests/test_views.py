from copy import deepcopy
from kinto.tests.core.support import unittest

from . import BaseWebTest

SUBSCRIPTION_RECORD = {
    "push": {"endpoint": "https://push.mozilla.com",
             "keys": {"auth": "authToken",
                      "p256dh": "encryptionKey"}},
    "triggers": {
        "/buckets/blocklists/collections/*/records": ["write"]
    }
}


class SubscriptionViewTest(BaseWebTest, unittest.TestCase):
    def test_authorization_mandatory_to_get_subscriptions(self):
        self.app.get("/notifications/webpush", status=401)

    def test_user_can_list_their_subscriptions(self):
        resp = self.app.get("/notifications/webpush", headers=self.headers)
        assert "data" in resp.json
        assert resp.json['data'] == []

    def test_user_can_add_subscription(self):
        resp = self.app.post_json("/notifications/webpush",
                                  {"data": SUBSCRIPTION_RECORD},
                                  headers=self.headers)
        record = resp.json['data']

        resp = self.app.get("/notifications/webpush", headers=self.headers)
        assert resp.json['data'] == [record]

    def test_malformed_subscription_get_rejected(self):
        self.app.post_json("/notifications/webpush",
                           {"data": {"malformed": "subscription"}},
                           headers=self.headers,
                           status=400)

    def test_trigger_that_register_a_wrong_resource_is_rejected(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers']['/wrong/endpoint'] = ['read']
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers,
                           status=400)

    def test_trigger_that_register_a_valid_bucket_is_accepted(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {'/buckets/endpoint': ['read']}
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers)

    def test_trigger_that_register_a_valid_collection_is_accepted(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {'/buckets/foo/collections/bar': ['read']}
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers)

    def test_trigger_that_register_a_valid_group_is_accepted(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {'/buckets/foo/groups/bar': ['read']}
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers)

    def test_trigger_that_register_a_valid_record_is_accepted(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {'/buckets/foo/collections/bar/records': ['read']}
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers)

    def test_trigger_that_register_a_invalid_record_is_rejected(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {'/buckets/foo/groups/bar/records': ['read']}
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers,
                           status=400)

    def test_trigger_that_register_a_valid_write_permission_is_accepted(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {
            '/buckets/foo/collections/bar/records': ['write']
        }
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers)

    def test_trigger_that_register_a_invalid_permission_is_rejected(self):
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['triggers'] = {
            '/buckets/foo/collections/bar/records': ['record:create']
        }
        self.app.post_json("/notifications/webpush",
                           {"data": record},
                           headers=self.headers,
                           status=400)

    def test_user_can_update_their_subscription(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        record = deepcopy(SUBSCRIPTION_RECORD)
        record['push']['endpoint'] = 'https://push.mozilla/newendpoint.com'
        resp = self.app.put_json('/notifications/webpush/%s' % record_id,
                                 {"data": record},
                                 headers=self.headers)
        endpoint = resp.json['data']['push']['endpoint']
        assert endpoint == 'https://push.mozilla/newendpoint.com'

    def test_user_can_modify_its_subscription_endpoint(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        body = {"push": {"endpoint": "https://push.mozilla/newendpoint.com",
                         "keys": SUBSCRIPTION_RECORD['push']['keys']}}
        resp = self.app.patch_json("/notifications/webpush/%s" % record_id,
                                   {"data": body},
                                   headers=self.headers)
        endpoint = resp.json['data']['push']['endpoint']
        assert endpoint == 'https://push.mozilla/newendpoint.com'

    def test_user_cannot_modify_list_of_subscription(self):
        self.app.put("/notifications/webpush",
                     {"data": SUBSCRIPTION_RECORD},
                     headers=self.headers,
                     status=405)

    def test_user_can_modify_their_trigger_action(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        body = {'triggers': {'/buckets/foo/collections/bar/records': ['read']}}
        resp = self.app.patch_json("/notifications/webpush/%s" % record_id,
                                   {"data": body},
                                   headers=self.headers)
        trigger = resp.json['data']['triggers']
        assert trigger == {'/buckets/foo/collections/bar/records': ['read']}

    def test_user_can_modify_trigger_to_register_a_valid_bucket(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        body = {'triggers': {'/buckets/endpoint': ['read']}}
        resp = self.app.patch_json("/notifications/webpush/%s" % record_id,
                                   {"data": body},
                                   headers=self.headers)
        trigger = resp.json['data']['triggers']
        assert trigger == {'/buckets/endpoint': ['read']}

    def test_user_can_modify_trigger_to_register_a_valid_collection(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        body = {'triggers': {'/buckets/foo/collections/bar': ['read']}}
        resp = self.app.patch_json("/notifications/webpush/%s" % record_id,
                                   {"data": body},
                                   headers=self.headers)
        trigger = resp.json['data']['triggers']
        assert trigger == {'/buckets/foo/collections/bar': ['read']}

    def test_user_can_modify_trigger_to_register_a_valid_group(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        body = {'triggers': {'/buckets/foo/groups/bar': ['read']}}
        resp = self.app.patch_json("/notifications/webpush/%s" % record_id,
                                   {"data": body},
                                   headers=self.headers)
        trigger = resp.json['data']['triggers']
        assert trigger == {'/buckets/foo/groups/bar': ['read']}

    def test_user_can_modify_trigger_to_register_a_valid_record(self):
        response = self.app.post_json("/notifications/webpush",
                                      {"data": SUBSCRIPTION_RECORD},
                                      headers=self.headers)
        record_id = response.json['data']['id']
        body = {'triggers': {'/buckets/foo/collections/bar/records': ['read']}}
        resp = self.app.patch_json("/notifications/webpush/%s" % record_id,
                                   {"data": body},
                                   headers=self.headers)
        trigger = resp.json['data']['triggers']
        assert trigger == {'/buckets/foo/collections/bar/records': ['read']}

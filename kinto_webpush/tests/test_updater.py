from .support import unittest

import kinto_updater
import mock
import pytest

SERVER_URL = "http://kinto-storage.org"


class BaseUpdaterTest(object):
    def _build_response(self, data, headers=None):
        if headers is None:
            headers = {}
        resp = {
            'data': data
        }
        return resp, headers


class UpdaterConstructorTest(unittest.TestCase, BaseUpdaterTest):

    @mock.patch('kinto_updater.signer.RSABackend')
    def test_signer_instance_defaults_to_rsa(self, backend):
        kinto_updater.Updater('bucket', 'collection',
                              SERVER_URL,
                              auth=('user', 'pass'),
                              settings=mock.sentinel.settings)
        backend.assert_called_with(mock.sentinel.settings)


class UpdaterDataValidityTest(unittest.TestCase, BaseUpdaterTest):

    def setUp(self):
        self.session = mock.MagicMock()
        self.endpoints = mock.MagicMock()
        self.signer_instance = mock.MagicMock()

    @mock.patch('kinto_updater.hasher.compute_hash')
    def test_data_validity_uses_configured_backend(self, compute_hash):
        updater = kinto_updater.Updater(
            'bucket', 'collection',
            auth=('user', 'pass'),
            session=self.session,
            signer_instance=self.signer_instance
        )
        compute_hash.return_value = '1234'

        records = {'1': {'id': '1', 'data': 'value'}}
        updater.check_data_validity(records, mock.sentinel.signature)
        self.signer_instance.verify.assert_called_with(
            '1234',
            mock.sentinel.signature
        )


class AddRecordsTest(unittest.TestCase, BaseUpdaterTest):

    def setUp(self):
        self.session = mock.MagicMock()
        self.signer_instance = mock.MagicMock()
        self.updater = kinto_updater.Updater(
            'bucket', 'collection',
            auth=('user', 'pass'),
            session=self.session,
            signer_instance=self.signer_instance
        )

    def test_add_records_fails_if_existing_collection_without_signature(self):
        records = [
            {'foo': 'bar'},
            {'bar': 'baz'},
        ]
        self.session.request.side_effect = [
            # First one returns the collection information (without sig).
            self._build_response({'last_modified': '1234'}),
            # Second returns the items in the collection.
            self._build_response([
                {'id': '1', 'value': 'item1'},
                {'id': '2', 'value': 'item2'}]
            ),
        ]

        with pytest.raises(kinto_updater.exceptions.UpdaterException):
            self.updater.add_records(records)

    @mock.patch('uuid.uuid4')
    def test_add_records_to_empty_collection(self, uuid4):
        records = [
            {'foo': 'bar'},
            {'bar': 'baz'},
        ]
        self.session.request.side_effect = [
            # First one returns the collection information.
            self._build_response({'last_modified': '1234'}),
            self._build_response([]),
        ]
        uuid4.side_effect = [1, 2]
        self.signer_instance.sign.return_value = '1234'

        self.updater.add_records(records)

        self.session.request.assert_called_with(
            'POST', '/batch', payload={'requests': [
                {
                    'body': {'data': {'foo': 'bar', 'id': '1'}},
                    'path': '/buckets/bucket/collections/collection/records/1',
                    'method': 'PUT',
                    'headers': {'If-None-Match': '*'}
                },
                {
                    'body': {'data': {'bar': 'baz', 'id': '2'}},
                    'path': '/buckets/bucket/collections/collection/records/2',
                    'method': 'PUT',
                    'headers': {'If-None-Match': '*'}
                },
                {
                    'body': {'data': {'signature': '1234'}},
                    'path': '/buckets/bucket/collections/collection',
                    'method': 'PATCH',
                }
            ]}
        )

    @mock.patch('kinto_updater.hasher.compute_hash')
    @mock.patch('uuid.uuid4')
    def test_add_records_to_existing_collection(self, uuid4, compute_hash):
        records = [
            {'foo': 'bar'},
            {'bar': 'baz'},
        ]
        self.session.request.side_effect = [
            # First one returns the collection information.
            self._build_response({'signature': 'sig',
                                  'last_modified': '1234'}),
            # Second returns the items in the collection.
            self._build_response([
                {'id': '1', 'value': 'item1'},
                {'id': '2', 'value': 'item2'}]
            ),
        ]
        uuid4.side_effect = [1, 2]
        self.signer_instance.sign.return_value = '1234'
        compute_hash.return_value = 'hash'

        self.updater.add_records(records)

        self.signer_instance.verify.assert_called_with('hash', 'sig')

        self.session.request.assert_called_with(
            'POST', '/batch', payload={'requests': [
                {
                    'body': {'data': {'foo': 'bar', 'id': '1'}},
                    'path': '/buckets/bucket/collections/collection/records/1',
                    'method': 'PUT',
                    'headers': {'If-None-Match': '*'}
                },
                {
                    'body': {'data': {'bar': 'baz', 'id': '2'}},
                    'path': '/buckets/bucket/collections/collection/records/2',
                    'method': 'PUT',
                    'headers': {'If-None-Match': '*'}
                },
                {
                    'body': {'data': {'signature': '1234'}},
                    'path': '/buckets/bucket/collections/collection',
                    'method': 'PATCH',
                }
            ]}
        )

    @mock.patch('kinto_updater.hasher.compute_hash')
    @mock.patch('uuid.uuid4')
    def test_add_records_can_update_existing_ones(self, uuid4, compute_hash):
        records = [
            {'id': '1', 'last_modified': '1234', 'foo': 'bar'},
            {'bar': 'baz'},
        ]
        self.session.request.side_effect = [
            # First one returns the collection information.
            self._build_response({'signature': 'sig',
                                  'last_modified': '1234'}),
            # Second returns the items in the collection.
            self._build_response([
                {'id': '1', 'value': 'item1'},
                {'id': '2', 'value': 'item2'}]
            ),
        ]
        uuid4.side_effect = [3, ]
        self.signer_instance.sign.return_value = '1234'
        compute_hash.return_value = 'hash'

        self.updater.add_records(records)

        self.signer_instance.verify.assert_called_with('hash', 'sig')

        self.session.request.assert_called_with(
            'POST', '/batch', payload={'requests': [
                {
                    'body': {'data': {'foo': 'bar', 'id': '1'}},
                    'path': '/buckets/bucket/collections/collection/records/1',
                    'method': 'PUT',
                    'headers': {'If-Match': '"1234"'}
                },
                {
                    'body': {'data': {'bar': 'baz', 'id': '3'}},
                    'path': '/buckets/bucket/collections/collection/records/3',
                    'method': 'PUT',
                    'headers': {'If-None-Match': '*'}
                },
                {
                    'body': {'data': {'signature': '1234'}},
                    'path': '/buckets/bucket/collections/collection',
                    'method': 'PATCH',
                }
            ]}
        )

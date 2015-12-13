from collections import OrderedDict

from .support import unittest

from kinto_updater import hasher


class HashComputingTest(unittest.TestCase):
    def test_records_are_not_altered(self):
        records = [
            {'foo': 'bar', 'last_modified': '12345', 'id': '1'},
            {'bar': 'baz', 'last_modified': '45678', 'id': '2'},
        ]
        hasher.compute_hash(records)
        assert records == [
            {'foo': 'bar', 'last_modified': '12345', 'id': '1'},
            {'bar': 'baz', 'last_modified': '45678', 'id': '2'},
        ]

    def test_order_doesnt_matters(self):
        hash1 = hasher.compute_hash([
            OrderedDict({'foo': 'bar', 'last_modified': '12345', 'id': '1'}),
            OrderedDict({'bar': 'baz', 'last_modified': '45678', 'id': '2'}),
        ])
        hash2 = hasher.compute_hash([
            OrderedDict({'last_modified': '45678', 'id': '2', 'bar': 'baz'}),
            OrderedDict({'foo': 'bar', 'id': '1', 'last_modified': '12345'}),
        ])

        assert hash1 == hash2

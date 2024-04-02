"""A simple fastAPI app, to be refactored"""

from typing import Callable, MutableMapping
from dataclasses import dataclass

URI_TYPE = str
StoreFactory = Callable[[URI_TYPE], MutableMapping]


# -------------------------------------------------------------------------------------
# The objects we want to dispatch as http services

def random_integer(smallest: int = 1, highest: int = 10):
    """Return a random integer between smallest and highest"""
    from random import randint

    return randint(smallest, highest)


def greeter(greeting: str, name: str = 'world', n: int = 1):
    """Return a greeting"""
    return '\n'.join(f"{greeting}, {name}!" for _ in range(n))


# A dict (which will be initialized with some data next)
# This dict should be able to be replaced with any MutableMapping interface 
# to any persisted data source, or aggregate thereof, 
# so it represents any data source/target a web service might have
backend_mall = {}


# -------------------------------------------------------------------------------------
# This section initializes the backend_mall with some data, in place

from copy import deepcopy

_backend_mall_init = {
    "alice": {
        'fruit': {"apple": 1, "banana": 2},
        'planets': {"mercury": 10, "venus": 20, "earth": 30},
    },
    "bob": {
        'food': {"apple": 1, "broccoli": 2, "carrot": 3},
        'cars': {"ford": 10, "toyota": 20},
        'colors': {'red': 100},
    },
}


def reset_backend_mall():
    """Reset the backend_mall to its initial state"""
    backend_mall.clear()
    backend_mall.update(deepcopy(_backend_mall_init))


reset_backend_mall()

# A util to get a user's data
def get_user_data(user: str):
    """Get the data for given user"""
    return backend_mall[user]


# -------------------------------------------------------------------------------------
# Ignore for now

DFLT_URI = 'test_uri'


def test_uri_to_store(uri: str = DFLT_URI):
    assert uri == DFLT_URI, f"Can only use uri={DFLT_URI} for now..."
    return backend_mall


@dataclass
class StoreAccess:
    """
    Delegator for MutableMapping, providing list, read, write, and delete methods.

    This is intended to be used in web services, offering nicer method names than
    the MutableMapping interface, and an actual list instead of a generator in
    the case of list.

    >>> s = StoreAccess.from_uri('test_uri')
    >>> s.list()
    ['alice', 'bob']

    """

    store: MutableMapping

    @classmethod
    def from_uri(cls, uri: URI_TYPE = DFLT_URI):
        """code that makes a MutableMapping interface for the data pointed to by uri"""
        if uri == DFLT_URI:
            store = backend_mall
            return cls(store)
        else:
            raise ValueError(f"Only one possible uri for now: {DFLT_URI}")

    def list(self):
        return list(self.store.keys())

    def read(self, key):
        return self.store[key]

    def write(self, key, value):
        self.store[key] = value

    def delete(self, key):
        del self.store[key]

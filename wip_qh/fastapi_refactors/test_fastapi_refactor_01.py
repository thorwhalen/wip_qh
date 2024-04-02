from fastapi.testclient import TestClient

from wip_qh.fastapi_refactors.fastapi_refactor_00 import backend_mall
from wip_qh.fastapi_refactors.utils_for_test_fastapi_refactor_01 import (
    fastapi_refactor_apps,
)
from typing import Union
from lkj import clog

DFLT_APP_INDEX = 1
apps = fastapi_refactor_apps()
default_app = apps[DFLT_APP_INDEX]


def test_fastapi_refactor_app(app=apps, verbose: Union[int, bool] = False):
    _clog = clog(verbose)
    if isinstance(verbose, int):
        verbose = verbose > 1
        __clog = clog(True)
    if isinstance(app, dict):
        for i, app in app.items():
            if i > 0:
                _clog(f"Testing app {i}")
                test_fastapi_refactor_app(app)
        return

    client = TestClient(app)

    def test_get_random_integer():
        __clog("    test_get_random_integer")
        response = client.get("/random_integer")
        assert response.status_code == 200
        assert isinstance(response.json(), int)

    def test_greeter():
        __clog("    test_greeter")
        response = client.get("/greeter/Hi/John")
        assert response.status_code == 200
        assert response.json() == "Hi, John!", f"Got: {response.json()=}"

    def test_get_store_list():
        __clog("    test_get_store_list")
        user = next(iter(backend_mall))
        keys = sorted(backend_mall[user].keys())

        response = client.get(f"/store_list/{user}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json() == keys, f"Got: {response.json()=}"

    def test_get_store_value():
        __clog("    test_get_store_value")
        user = next(iter(backend_mall))
        keys = sorted(backend_mall[user].keys())
        key = keys[0]
        value = backend_mall[user][key]

        response = client.get(f"/store_get/{user}/{key}")
        assert response.status_code == 200
        assert response.json() == value, f"Got: {response.json()=}"

    def test_set_store_value():
        __clog("    test_set_store_value")
        user = next(iter(backend_mall))
        keys = sorted(backend_mall[user].keys())
        key = keys[0]

        response = client.post("/store_set/user1/key1", json={"value": "some_value"})
        assert response.status_code == 200
        assert response.json() == {"message": "Value set successfully"}
        assert backend_mall[user][key] == "some_value"
        # clean up (TODO: do with with block instead)
        del backend_mall[user][key]

    test_get_random_integer()
    test_greeter()
    test_get_store_list()
    test_get_store_value()

    # TODO: add test for set_store_value when backend is persistent
    # test_set_store_value()

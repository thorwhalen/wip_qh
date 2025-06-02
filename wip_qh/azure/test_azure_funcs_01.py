"""
Test the 01 version of the Azure Functions code.
"""

import json
import azure.functions as af


def routes_of_app(app):
    """
    Yields (name, func) pairs for the routes of azure.functions app.
    (Note: Tested for `azure-functions==1.21.3`)
    """
    for route in app._function_builders:
        yield route._function._name, route._function._func


def test_app(app):
    # Check that the app has the expected routes.
    routes = dict(routes_of_app(app))

    list_funcs = routes['list_funcs']
    apply_func = routes['apply_func']

    test_list_funcs_route(list_funcs)
    test_apply_func_plus_one(apply_func)
    test_apply_func_times_two(apply_func)
    test_apply_func_invalid_arg(apply_func)
    test_apply_func_unknown_function(apply_func)


def test_requests(root_url='http://localhost:7071/api/'):
    from urllib.parse import urljoin
    from functools import partial
    import requests

    get_url = partial(urljoin, root_url)

    r1 = requests.get(get_url('list_funcs'))
    assert r1.status_code == 200
    assert r1.json() == ['plus_one', 'times_two']

    r2 = requests.post(get_url('apply_func'), json={'func_name': 'plus_one', 'arg': 42})
    assert r2.status_code == 200
    assert r2.json() == 43


def test_list_funcs_route(list_funcs):
    # Create a dummy HTTP GET request for the list_funcs route.
    req = af.HttpRequest(method="GET", url="/api/list_funcs", params={}, body=None)
    resp = list_funcs(req)
    assert resp.status_code == 200
    data = json.loads(resp.get_body())
    assert "plus_one" in data
    assert "times_two" in data


def test_apply_func_plus_one(apply_func):
    # Test using the 'plus_one' function.
    req = af.HttpRequest(
        method="GET",
        url="/api/apply_func",
        params={"arg": "3", "func_name": "plus_one"},
        body=None,
    )
    resp = apply_func(req)
    assert resp.status_code == 200
    data = json.loads(resp.get_body())
    # plus_one(3) should return 4.
    assert data == 4


def test_apply_func_times_two(apply_func):
    # Test using the 'times_two' function.
    req = af.HttpRequest(
        method="GET",
        url="/api/apply_func",
        params={"arg": "3", "func_name": "times_two"},
        body=None,
    )
    resp = apply_func(req)
    assert resp.status_code == 200
    data = json.loads(resp.get_body())
    # As implemented, times_two(3) returns 4.
    assert data == 4


def test_apply_func_invalid_arg(apply_func):
    # Test error handling with a non-numeric argument.
    req = af.HttpRequest(
        method="GET",
        url="/api/apply_func",
        params={"arg": "abc", "func_name": "plus_one"},
        body=None,
    )
    resp = apply_func(req)
    assert resp.status_code == 400


def test_apply_func_unknown_function(apply_func):
    # Test handling of an unknown function name.
    req = af.HttpRequest(
        method="GET",
        url="/api/apply_func",
        params={"arg": "3", "func_name": "nonexistent"},
        body=None,
    )
    resp = apply_func(req)
    assert resp.status_code == 404

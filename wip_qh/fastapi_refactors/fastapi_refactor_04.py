"""
Here, we'll try out a few "convention over configuration" tricks to make the 
configurationof the FastAPI app more concise and less error-prone. 

"""

from fastapi import Query, Body
from typing import Any
from wip_qh.fastapi_refactors.utils_for_fastapi_refactor_03 import fast_api_app

# get the resourcs we'll be dispatching to web services
from wip_qh.fastapi_refactors.fastapi_refactor_00 import (
    random_integer,
    greeter,
    get_store_list,
    get_store_value,
    set_store_value,
)

# Configurations for each endpoint
expected_route_specs = {
    random_integer: {
        "api_route_kwargs": dict(methods=['GET'], path="/random_integer"),
        "defaults": {"smallest": Query(1), "highest": Query(10)},
    },
    greeter: {
        "api_route_kwargs": dict(methods=['GET'], path="/greeter/{greeting}"),
        "defaults": {"name": Query("world"), "n": Query(1)},
    },
    get_store_list: {
        "api_route_kwargs": {"methods": ['GET'], "path": "/store_list/{user}"}
    },
    get_store_value: {
        "api_route_kwargs": {"methods": ['GET'], "path": "/store_get/{user}"},
        "defaults": {"key": Query()},
    },
    set_store_value: {
        "api_route_kwargs": {"methods": ['POST'], "path": "/store_set/{user}"},
        "defaults": {"key": Query(), "value": Body(embed=True)},
    },
}

from i2 import mk_sentinel
from copy import deepcopy
from typing import VT, KT, Callable, Union

NotProvided = mk_sentinel('NotProvided')

DFLT_API_ROUTE_KWARGS = dict(methods=['GET'])

EndpointBackend = Callable
ApiRouteKwargs = dict
DefaultType = Union[VT, Callable[[EndpointBackend, ApiRouteKwargs], VT]]


def complete_route_specs(route_specs: dict):
    route_specs = deepcopy(route_specs)
    for func, spec in route_specs.items():
        spec['api_route_kwargs'] = resolve_api_route_kwargs(func, spec['api_route_kwargs'])
    return route_specs


def resolve_api_route_kwargs(
    func: EndpointBackend, api_route_kwargs, *, defaults=DFLT_API_ROUTE_KWARGS
):
    api_route_kwargs = deepcopy(api_route_kwargs)

    for field in ['methods']:
        if field not in api_route_kwargs and field in defaults:
            api_route_kwargs[field] = _resolve_value(
                func, api_route_kwargs, field, defaults[field]
            )
    return api_route_kwargs


def _resolve_value(
    func: EndpointBackend, api_route_kwargs: dict, field: str, default: DefaultType
):
    value = api_route_kwargs.get(field, NotProvided)
    if value is NotProvided:
        value = default(func, complete_route_specs) if callable(default) else default
    return value


app = fast_api_app(expected_route_specs)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

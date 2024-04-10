"""
Here, we make the apply_wrappers mechanism more general and flexible.

Note that FastApi methods for http methods (get, post, put, etc.) are just convenience
methods that call the underlying add_api_route method, which itself is a convenience 
method that uses the APIRoute class to create a route. We'll use the latter directly,
so as to have more control over the configuration of the route.

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
route_specs = {
    random_integer: {
        "api_route_kwargs": dict(methods=['GET'], path="/random_integer"),
        "defaults": {"smallest": Query(1), "highest": Query(10)},
    },
    greeter: {
        "api_route_kwargs": dict(methods=['GET'], path="/greeter/{greeting}"),
        "defaults": {"name": Query("world"), "n": Query(1)},
    },
    get_store_list: {
        "api_route_kwargs": {"methods": 'get', "path": "/store_list/{user}"}
    },
    get_store_value: {
        "api_route_kwargs": {"methods": 'get', "path": "/store_get/{user}"},
        "defaults": {"key": Query()},
    },
    set_store_value: {
        "api_route_kwargs": {"methods": 'post', "path": "/store_set/{user}"},
        "defaults": {"key": Query(), "value": Body(embed=True)},
    },
}


app = fast_api_app(route_specs)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

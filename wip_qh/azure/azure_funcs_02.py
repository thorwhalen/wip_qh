"""
The following is what a straightforward implementation of the web service 
(or microservice), serving the `list_funcs` and `apply_func` might look like.
The way you'd see a "Hello, World!" in a Azure Functions tutorial.
"""

from i2 import Sig


from wip_qh.azure.core_logic import (
    list_funcs as _list_funcs,
    apply_func as _apply_func,
)

import json
import azure.functions as af

# Create the Function App with anonymous access.
app = af.FunctionApp(http_auth_level=af.AuthLevel.ANONYMOUS)


from functools import partial
from dataclasses import dataclass
from typing import Callable, Any, Mapping

FunctionOutput = Any


@dataclass
class AzureWrapOld:
    func: Callable
    extract_params: Callable[[af.HttpRequest], dict]

    def __call__(self, req: af.HttpRequest) -> af.HttpResponse:
        try:
            params = self.extract_params(req)
            result = self.func(**params)
            return af.HttpResponse(
                json.dumps(result), status_code=200, mimetype="application/json"
            )
        except KeyError as e:
            return af.HttpResponse(str(e), status_code=404)
        except Exception as e:
            return af.HttpResponse(str(e), status_code=400)


def default_extract_params(
    req: af.HttpRequest,
) -> dict:
    """
    Default function to extract function params from a request object
    """
    try:
        body = req.get_json()
    except Exception:
        body = {}
    return {**req.params, **body}


def http_response(
    output: FunctionOutput = None,
    *,
    cast: Callable = json.dumps,
    status_code: int = 200,
    mimetype="application/json",
) -> af.HttpResponse:
    if output is None:
        return partial(
            http_response, cast=cast, status_code=status_code, mimetype=mimetype
        )
    return af.HttpResponse(cast(output), status_code=status_code, mimetype=mimetype)


from i2 import Wrap


@dataclass
class AzureWrap:
    func: Callable
    ingress: Callable[[af.HttpRequest], dict]
    egress: Callable[[FunctionOutput], af.HttpResponse]
    exception_handles: dict

    @property
    def __name__(self):
        return self.func.__name__

    def __call__(self, req: af.HttpRequest) -> af.HttpResponse:
        try:
            params = self.ingress(req)  # extract params
            result = self.func(  # call the function
                **params
            )  # if positional args are needed, or there are extra params we can use i2.call_forgivingly here
            return self.egress(result)
        except tuple(self.exception_handles) as e:
            for exc_type, exc_handle in self.exception_handles.items():
                if isinstance(e, exc_type):
                    body = exc_handle['body'](e)
                    remaining_kwargs = {
                        k: v for k, v in exc_handle.items() if k != 'body'
                    }
                    return af.HttpResponse(body, **remaining_kwargs)


from i2 import double_up_as_factory, name_of_obj


def extract_and_cast(req, *, cast: dict = (), extract=default_extract_params):
    cast = dict(cast)
    params = extract(req)
    for param_name, cast_func in cast.items():
        if param_name in params:
            params[param_name] = cast_func(params[param_name])
    return params


@double_up_as_factory
def azure_wrap(
    func: Callable = None,
    *,
    ingress: Callable[[af.HttpRequest], dict] = default_extract_params,
    egress: Callable[[FunctionOutput], af.HttpResponse] = http_response,
    exception_handles: dict = {
        KeyError: dict(body=str, status_code=404),
        Exception: dict(body=str, status_code=400),
    },
) -> AzureWrap:
    if isinstance(ingress, dict):
        cast = ingress
        ingress = partial(extract_and_cast, cast=cast)
    elif ingress is None:
        ingress = default_extract_params

    return AzureWrap(
        func,
        ingress=ingress,
        egress=egress,
        exception_handles=exception_handles,
    )


def default_app_factory():
    return af.FunctionApp(http_auth_level=af.AuthLevel.ANONYMOUS)


def add_app_route(func, *, app=None, route=None, methods=("GET", "POST"), ingress=None):
    if app is None:
        app = default_app_factory()
    if route is None:
        route = name_of_obj(func)
    app_route = app.route(route=route, methods=methods)
    _azure_wrap = azure_wrap(ingress=ingress)
    return app_route(_azure_wrap(func))


def dispatch_funcs(funcs, *, app=None, ingress=()):
    ingress = dict(ingress)
    if not isinstance(funcs, Mapping):
        funcs = {name_of_obj(func): func for func in funcs}
    if app is None:
        app = default_app_factory()
    for route, func in funcs.items():
        _ingress = ingress.get(func, None) or ingress.get(route, None)
        add_app_route(func, app=app, route=route, ingress=_ingress)
    return app


# --- Azure Functions route definitions ---

# wip_qh/azure/azure_funcs_02.py
import azure.functions as af
from wip_qh.azure.core_logic import list_funcs, apply_func

app = dispatch_funcs([list_funcs, apply_func], ingress=dict(apply_func={'arg': int}))


# app = af.FunctionApp(http_auth_level=af.AuthLevel.ANONYMOUS)

# add_app_route(list_funcs, app=app)
# add_app_route(apply_func, app=app, ingress={'arg': int})


# import azure.functions as af
# from wip_qh.azure.core_logic import list_funcs as _list_funcs, apply_func as _apply_func


# app = af.FunctionApp(http_auth_level=af.AuthLevel.ANONYMOUS)

# )
# # Route for listing available functions.
# @app.route(route="list_funcs", methods=["GET", "POST"])
# @azure_wrap  # No parameters are needed.
# def list_funcs():
#     return _list_funcs()


# # Route for applying a function to an input.
# @app.route(route="apply_func", methods=["GET", "POST"])
# @azure_wrap(ingress={'arg': int})
# def apply_func(arg, func_name):
#     return _apply_func(arg=arg, func_name=func_name)

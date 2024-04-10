"""
Note that FastApi methods for http methods (get, post, put, etc.) are just convenience
methods that call the underlying add_api_route method, which itself is a convenience 
method that uses the APIRoute class to create a route. We'll use the latter directly,
so as to have more control over the configuration of the route.

Contents:

Main: 
- add_routes_to_app: add routes to a FastAPI app
- fast_api_app: create a FastAPI app with routes

Helpers:
- a few unused types for http methods and route method keywords
- model_from_function: generates a Pydantic model based on the signature of the input function
- validate_dict_with_model: validate the data against a Pydantic model
- mk_func_input_validator: make a validator for a function's input parameters 
    (using model_from_function and validate_dict_with_model)
- mk_endpoint: wrap func to prepare for use as an endpoint
- add_defaults: add defaults to a dictionary if they are not already present
- mk_api_route_kwargs: make the kwargs for the APIRoute constructor

"""

# -------------------------------------------------------------------------------------
# utils


def value_transformed_dict_equality(d1=None, d2=None, value_transformer=lambda x: x):
    """
    Recursively compare two dictionaries,
    applying a value transformer to the values before comparison when the value is not
    itself a dict

    >>> d1 = {'a': 'a', 'b': {'c': 'bc'}}
    >>> d2 = {'a': 'A', 'b': {'c': 'bC'}}
    >>> d1 == d2
    False
    >>> compare = value_transformed_dict_equality(value_transformer=str.upper)
    >>> compare(d1, d2)
    True
    """
    if d1 is None and d2 is None:
        from functools import partial

        return partial(
            value_transformed_dict_equality, value_transformer=value_transformer
        )
    else:
        if d1.keys() != d2.keys():
            return False
        for k in d1:
            if isinstance(d1[k], dict):
                if not value_transformed_dict_equality(d1[k], d2[k], value_transformer):
                    return False
            else:
                if value_transformer(d1[k]) != value_transformer(d2[k]):
                    return False
        return True


# TODO: Handle all methods (not only get and post) and method arguments (not only path)
# TODO: Validate configs (use pydantic)
# TODO: Add name=name_of_obj(function) to method kwargs
#    (fastapi takes name from type of wrap instance, so always Wrap)
# TODO: Need to extract and (inject in Query and Body) the original defaults
#  from the underlying function (the "endpoint") to avoid manual duplication,
#  therefore making the configuration more concise and less error-prone.

from fastapi.routing import APIRoute
from fastapi import FastAPI
from pydantic import BaseModel, create_model, Field, ValidationError
from typing import Literal, Dict, Any, Callable, Type, T, Union, Iterable
from functools import partial
import inspect
from i2 import Sig, wrap, asis, name_of_obj


HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"
]

# Get APIRoute argument names
_api_route_arg_names = tuple(Sig(APIRoute).names)
RouteMethodKeyword = Literal[_api_route_arg_names]  # type: ignore

RouteSpec = Dict[RouteMethodKeyword, Any]


def model_from_function(
    func: Callable, *, name=None, arbitrary_types_allowed=True
) -> Type[BaseModel]:
    """
    Generates a Pydantic model based on the signature of the input function.
    Parameters without type annotations default to typing.Any.

    :param func: The function from which to generate the Pydantic model.
    :return: A Pydantic model class ready to be instantiated.

    >>> def example_function(name: str, age: int, nickname: str = "No nickname", weight: float = 70.5):
    ...     pass
    >>> Model = model_from_function(example_function)
    >>> valid_data = {"name": "John Doe", "age": 30, "nickname": "Johnny", "weight": 80.0}
    >>> invalid_data = {"name": "Jane Doe", "age": "thirty", "weight": "heavy"}  # 'age' should be int, 'weight' should be float, 'nickname' is missing
    >>> model_instance = Model(**valid_data)
    >>> print(model_instance.name, model_instance.age)
    John Doe 30
    >>> try:
    ...     Model(**invalid_data)
    ... except ValidationError as e:
    ...     print("Validation failed")
    Validation failed
    """
    parameters = inspect.signature(func).parameters
    fields = {
        name: (
            (param.annotation if param.annotation != inspect._empty else Any),
            (
                Field(default=param.default)
                if param.default is not inspect._empty
                else Field(...)
            ),
        )
        for name, param in parameters.items()
    }

    name = name or (name_of_obj(func) + "_pydantic_model")
    model_attrs = {_name: field for _name, field in fields.items()}

    if not arbitrary_types_allowed:
        return create_model(name, **model_attrs)
    else:

        class Config:
            arbitrary_types_allowed = True

        return create_model(name, __config__=Config, **model_attrs)


def validate_dict_with_model(data: dict, model: Type[BaseModel]) -> dict:
    """
    Validate the data against a Pydantic model.
    If the data is invalid, a ValidationError is raised.
    If not, the original data is returned
    """
    _ = model(**data)
    return data  # Return the data if there's no errors


def mk_func_input_validator(func: Callable) -> Callable:
    """
    Make a validator for a function's input parameters.
    Uses a pydantic model generated from the function's signature to validate the input.
    """
    func_input_model = model_from_function(func)
    return partial(validate_dict_with_model, model=func_input_model)


def mk_endpoint(func, defaults):
    """
    Wrap func to prepare for use as an endpoint.

    Namely, change the defaults to be request parameters (Path, Query, Body, etc.)
    """
    new_sig = Sig(func).ch_defaults(**defaults)
    # Wrap the function to apply changes to the wrapper; not the function itself.
    _func = wrap(func)
    # apply the sigature to the wrapped function
    _func = new_sig(_func)
    return _func


def add_defaults(d: dict, dflt: dict):
    """
    Add defaults to a dictionary if they are not already present.

    This is a shallow copy operation.

    >>> add_defaults({'a': 10}, dflt={'a': 1, 'b': 2})
    {'a': 10, 'b': 2}

    """
    result = dflt.copy()
    result.update(d)
    return result


def mk_api_route_kwargs(
    func,
    config,
    *,
    config_validator: Callable[[T], T] = asis,
    dflt_methods=['GET', 'POST'],
):
    endpoint = mk_endpoint(func, defaults=config.get('defaults', {}))
    api_route_kwargs = config.get('api_route_kwargs', {})
    name = name_of_obj(func)
    dflt_api_route_kwargs = dict(
        endpoint=endpoint,
        path=f"/{name}",
        methods=dflt_methods,
        name=name,
        description=getattr(func, '__doc__', ''),
    )
    api_route_kwargs = add_defaults(api_route_kwargs, dflt_api_route_kwargs)
    try:
        api_route_kwargs = config_validator(api_route_kwargs)
    except ValidationError as e:
        raise ValueError(f"Error validating config for {name}: {e}")

    return api_route_kwargs


def _ensure_list(x):
    if isinstance(x, str):
        return [x]
    return x


def _ensure_list_of_upper_case_strings(x):
    if isinstance(x, str):
        return [x.upper()]
    return list(map(str.upper, x))


MethodsType = Union[str, Iterable[str]]


@(Sig(APIRoute).ch_annotations(methods=MethodsType))
def dflt_mk_route(*args, **kwargs):
    kwargs['methods'] = _ensure_list_of_upper_case_strings(kwargs['methods'])
    return APIRoute(*args, **kwargs)


# TODO: Make the validation work!!
def add_routes_to_app(
    app,
    route_specs,
    *,
    dflt_methods=['GET', 'POST'],
    mk_route: Callable = dflt_mk_route,
):
    config_validator = mk_func_input_validator(mk_route)
    _mk_api_route_kwargs = partial(
        mk_api_route_kwargs,
        dflt_methods=dflt_methods,
        config_validator=config_validator,
    )
    route_kwargs = map(_mk_api_route_kwargs, *zip(*route_specs.items()))
    routes = [mk_route(**kwargs) for kwargs in route_kwargs]
    app.routes.extend(routes)
    return app


def fast_api_app(routes, *, app: FastAPI = None):
    app = app or FastAPI()
    add_routes_to_app(app, routes)
    return app

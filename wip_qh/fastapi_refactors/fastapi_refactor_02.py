"""
In this module, we refactor the fastapi_refactor_01.py module to use a 
configuration dictionary to define the configurations for each endpoint. 
This is a step towards making the refactoring process more automated and less manual.

Our configuration here will specify the method and path that is needed to create 
the app.get or app.post decorators. We will also specify the default values for
the parameters of the function, which are used to create the Query or Body objects.

For example, instead of writing:

```python
@app.get("/greeter/{greeting}")
def _greeter(
    greeting: str,
    name: str = Query('world'),
    n: int = Query(1),
):
    return greeter(greeting, name, n)
```

to wrap the `greeter` function, we will seperate the configuration information,
placing it in a configs object, 

```python

configs = {
    ...
    greeter: {
        "method": "get",
        "path": "/greeter/{greeting}",
        "defaults": {"name": Query("world"), "n": Query(1)},
    },
    ...
}
```

and then use this information to wrap the function, like so:

```python
apply_wrappers(app, configs)
```

"""

from fastapi import FastAPI
from fastapi import Query, Body
from typing import Any
from i2 import Sig, wrap

# -------------------------------------------------------------------------------------
# utils

# TODO: Handle all methods (not only get and post) and method arguments (not only path)
# TODO: Validate configs (use pydantic)
# TODO: Add name=name_of_obj(function) to method kwargs
#    (fastapi takes name from type of wrap instance, so always Wrap)
# TODO: Need to extract and (inject in Query and Body) the original defaults
#  from the underlying function (the "endpoint") to avoid manual duplication,
#  therefore making the configuration more concise and less error-prone.
def apply_wrappers(app, configs):
    for function, config in configs.items():
        # Compute the new sig
        new_defaults = config.get('defaults', {})
        new_sig = Sig(function).ch_defaults(**new_defaults)
        # Wrap the function to apply changes to the wrapper; not the function itself.
        _function = wrap(function)
        # apply to the wrapper
        _function = new_sig(_function)
        # apply app decorators
        if config['method'] == 'get':
            app.get(config['path'])(_function)
        elif config['method'] == 'post':
            app.post(config['path'])(_function)


# -------------------------------------------------------------------------------------
# making the app

from wip_qh.fastapi_refactors.fastapi_refactor_00 import (
    random_integer,
    greeter,
    get_store_list,
    get_store_value,
    set_store_value,
)

app = FastAPI()


# Configurations for each endpoint
configs = {
    random_integer: {
        "method": "get",
        "path": "/random_integer",
        "defaults": {"smallest": Query(1), "highest": Query(10)},
    },
    greeter: {
        "method": "get",
        "path": "/greeter/{greeting}",
        "defaults": {"name": Query("world"), "n": Query(1)},
    },
    get_store_list: {"method": 'get', "path": "/store_list/{user}"},
    get_store_value: {
        "method": 'get',
        "path": "/store_get/{user}",
        "defaults": {"key": Query()},
    },
    set_store_value: {
        "method": 'post',
        "path": "/store_set/{user}",
        "defaults": {"key": Query(), "value": Body(..., embed=True)},
    },
}


apply_wrappers(app, configs)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

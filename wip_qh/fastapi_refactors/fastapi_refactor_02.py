"""A simple fastAPI app, to be refactored"""

from fastapi import FastAPI
from typing import Any

# Assuming these are defined elsewhere
from wip_qh.fastapi_refactors.fastapi_refactor_00 import (
    random_integer,
    greeter,
    get_user_data,
)

app = FastAPI()


# Function definitions remain the same compared to fastapi_refactor_01
def get_random_integer():
    return random_integer()


def greet(greeting: str, name: str):
    return greeter(greeting, name)


def get_store_list(user: str):
    store = get_user_data(user)
    return list(store)


def get_store_value(user: str, key: str):
    store = get_user_data(user)
    return store[key]


def set_store_value(user: str, key: str, value: Any):
    store = get_user_data(user)
    store[key] = value
    return {"message": "Value set successfully"}


# Configurations for each endpoint
configs = {
    get_random_integer: {"method": 'get', "path": "/random_integer"},
    greet: {"method": 'get', "path": "/greeter/{greeting}"},
    get_store_list: {"method": 'get', "path": "/store_list/{user}"},
    get_store_value: {"method": 'get', "path": "/store_get/{user}"},
    set_store_value: {"method": 'post', "path": "/store_set/{user}"},
}


# TODO: Handle all methods (not only get and post) and method arguments (not only path)
# TODO: Validate configs
def apply_decorators_to_app(app, configs):
    for function, config in configs.items():
        if config['method'] == 'get':
            app.get(config['path'])(function)
        elif config['method'] == 'post':
            app.post(config['path'])(function)


apply_decorators_to_app(app, configs)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

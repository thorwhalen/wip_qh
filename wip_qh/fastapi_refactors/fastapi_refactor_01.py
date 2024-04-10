"""A simple fastAPI app, to be refactored"""

from typing import Any, Optional
from fastapi import FastAPI, Query, Path, Body
from typing import Any
from wip_qh.fastapi_refactors.fastapi_refactor_00 import (
    random_integer,
    greeter,
    get_store_list,
    get_store_value,
    set_store_value,
)

app = FastAPI()


# @app.get("/random_integer")
# def _random_integer():
#     return random_integer()


# @app.get("/greeter/{greeting}/{name}")
# def _greeter(greeting: str, name: str):
#     return greeter(greeting, name)


@app.get("/random_integer")
def _random_integer(
    smallest: int = Query(1),
    highest: int = Query(10),
):
    """Endpoint to get a random integer within a range"""
    return random_integer(smallest, highest)


@app.get("/greeter/{greeting}")
def _greeter(
    greeting: str,  # extract name from path
    name: str = Query('world'),  # extract name from query string (default is 'world')
    n: int = Query(1),
):
    """Endpoint to return a greeting"""
    return greeter(greeting, name, n)


@app.get("/store_list/{user}")
def _get_store_list(user: str):
    return get_store_list(user)


@app.get("/store_get/{user}")
def _get_store_value(user: str, key: str = Query()):
    return get_store_value(user, key)


@app.post("/store_set/{user}")
def _set_store_value(
    user: str,
    key: str = Query(),
    value=Body(..., imbed=True),  # extract value from body
):
    value = value['value']  # ingress transformation
    return set_store_value(user, key, value)


this_file_name = __file__.split("/")[-1].split(".")[0]
# print(this_file_name)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

    # uvicorn.run(
    #     f"app:{this_file_name}",
    #     host="0.0.0.0",
    #     port=8000,
    #     reload=True,
    #     log_level="debug",
    # )

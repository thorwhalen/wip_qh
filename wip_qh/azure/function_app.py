"""
The following is what a straightforward implementation of the web service 
(or microservice), serving the `list_funcs` and `apply_func` might look like.
The way you'd see a "Hello, World!" in a Azure Functions tutorial.
"""

from wip_qh.azure.core_logic import (
    list_funcs as _list_funcs,
    apply_func as _apply_func,
)

import json
import azure.functions as af

# Create the Function App with anonymous access.
app = af.FunctionApp(http_auth_level=af.AuthLevel.ANONYMOUS)


# --- Azure Functions route definitions ---


@app.route(route="list_funcs", methods=["GET"])
def list_funcs(req: af.HttpRequest) -> af.HttpResponse:
    names = _list_funcs()
    return af.HttpResponse(
        json.dumps(names), status_code=200, mimetype="application/json"
    )


@app.route(route="apply_func", methods=["GET", "POST"])
def apply_func(req: af.HttpRequest) -> af.HttpResponse:
    # Attempt to extract 'arg' either from query parameters or JSON body.
    try:
        arg = req.params.get("arg")
        if not arg:
            req_body = req.get_json()
            arg = req_body.get("arg")
    except ValueError:
        return af.HttpResponse("Invalid request body", status_code=400)

    # Extract the function name (defaulting to 'plus_one').
    func_name = req.params.get("func_name")
    if not func_name:
        try:
            req_body = req.get_json()
            func_name = req_body.get("func_name")
        except Exception:
            raise KeyError("Function name not found")

    # Convert 'arg' to an integer.
    try:
        arg = int(arg)
    except Exception:
        return af.HttpResponse("Invalid arg value", status_code=400)

    try:
        result = _apply_func(arg=arg, func_name=func_name)
        return af.HttpResponse(
            json.dumps(result), status_code=200, mimetype="application/json"
        )
    except KeyError:
        return af.HttpResponse("Function not found", status_code=404)

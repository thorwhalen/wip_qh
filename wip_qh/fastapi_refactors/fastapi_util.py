"""Utils using FastAPI"""

from i2 import Sig
from fastapi import Path, Query, Header, Cookie, Body, Form, File

request_parameters_classes = [Path, Query, Header, Cookie, Body, Form, File]

# a dcit of the request parameters classes' signatures
request_params_sigs = {cls.__name__: Sig(cls) for cls in request_parameters_classes}
# a dict of the request parameters classes' arguments (and inspect.Parameter objects)
request_params_kwargs = {
    name: {p.name: p for p in sig.params} for name, sig in request_params_sigs.items()
}

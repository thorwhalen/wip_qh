"""Refactoring an azure functions app to use SoC reusable tools"""

import azure.functions as af
from ..azure_funcs_01 import app

def main(req: af.HttpRequest, context: af.Context) -> af.HttpResponse:
    return app(req, context)

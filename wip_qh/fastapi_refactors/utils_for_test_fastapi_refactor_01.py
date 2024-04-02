import pkgutil


def list_modules(package_name="wip_qh.fastapi_refactors", filt=None):
    """List all modules of package_name"""

    def gen():
        package = __import__(package_name, fromlist=["dummy"])
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            yield module_name

    return filter(filt, gen())


def fastapi_refactor_apps():
    """Yield all (i, app) pairs for the fastapi refactor apps"""

    # loop through all (existing) modules that have the form
    # "wip_qh.fastapi_refactors.fastapi_refactor_**.py"
    # import app from them, and return the {i: app, ...} dict
    def i_and_app():
        module_names = sorted(
            list_modules(filt=lambda x: x.startswith("fastapi_refactor_"))
        )
        for module_name in module_names:
            # extract the number after fastapi_refactor_**
            i = int(module_name.split("_")[-1])
            if i > 0:
                # import "app" from the module
                app = __import__(
                    f"wip_qh.fastapi_refactors.{module_name}", fromlist=["app"]
                ).app
                yield i, app

    return dict(i_and_app())

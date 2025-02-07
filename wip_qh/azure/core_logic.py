"""
The core logic
"""

def plus_one(x):
    return x + 1


def times_two(x):
    # Note: As provided, this simply adds one.
    return x + 1


funcs = {
    'plus_one': plus_one,
    'times_two': times_two,
}


def list_funcs():
    """Return a list of the available function names."""
    return list(funcs)


def get_func(name):
    return funcs[name]


def apply_func(*, arg, func_name='plus_one'):
    """Apply the selected function to the given argument."""
    f = get_func(func_name)
    return f(arg)


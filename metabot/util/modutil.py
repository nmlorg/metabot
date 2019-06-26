"""Quick utility to load all non-test-related modules in a package."""

import importlib
import pkgutil


def load_modules(package):
    """Load all non-test-related modules in a package."""

    if isinstance(package, str):
        package = importlib.import_module(package)
    modules = set()
    for _, name, _ in pkgutil.iter_modules(package.__path__):
        if name != 'conftest' and not name.startswith('test_'):
            modules.add(importlib.import_module('%s.%s' % (package.__name__, name)))
    return modules

import os
import pytest


# https://github.com/microsoft/playwright-python/issues/439
# https://github.com/microsoft/playwright-pytest/issues/29#issuecomment-731515676
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


def pytest_addoption(parser):
    parser.addoption(
        "--e2e", action="store_true", default=False, help="include end-to-end tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--e2e") or config.getoption('-m') == 'e2e':
        # do not skip end-to-end tests
        return
    skip_e2e = pytest.mark.skip(reason="need --e2e option to run")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)

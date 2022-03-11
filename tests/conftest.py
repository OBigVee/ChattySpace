import pytest


@pytest.fixture(autouse=True)
def setup(fn_isolation):
    """
    Isolation setup fixture.
    This ensures that each test runs against the same base environment.
    """
    pass


@pytest.fixture(scope="module")
def chat(accounts, Chat):
    """
    Yield a `Contract` object for the Chat contract.
    """
    yield accounts[0].deploy(Chat)
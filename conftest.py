import pytest


@pytest.fixture
def sb(request):
    from seleniumbase import SB
    with SB(uc=True, headless=True) as sb:
        yield sb


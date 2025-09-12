import os

def test_default_mode_is_local():
    # Ensures local is default
    assert os.getenv("USE_AWS", "false").lower() == "false"

def test_no_public_resources_placeholder():
    # Placeholder: in real IaC tests, assert policies deny public access
    assert True

import re
from phases._util_import import safe_import  # small helper below
from pathlib import Path

# Ensure import works whether repo root or exercise folder
RmClient = safe_import("phases/1b-exercise-rmapi/rm_client_skeleton.py", "RmClient")

def test_list_page_basic():
    c = RmClient()
    p = c.list_characters(page=1)
    assert p.info.count > 0
    assert len(p.results) > 0
    assert isinstance(p.results[0].name, str)

def test_detail_by_id():
    c = RmClient()
    d = c.get_character(1)
    assert d["id"] == 1
    assert "name" in d and isinstance(d["name"], str)

def test_search_by_name():
    c = RmClient()
    d = c.get_character("rick")
    assert "Rick" in d["name"]

def test_error_shape():
    c = RmClient()
    try:
        c.get_character(999999)
    except Exception as e:
        # should be our APIError with status and message
        s = str(e)
        assert "HTTP 404" in s
        assert ("There is nothing here" in s) or ("Character not found" in s)
    else:
        raise AssertionError("Expected an error for non-existent id")


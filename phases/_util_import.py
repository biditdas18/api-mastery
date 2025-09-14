# Drop this in phases/_util_import.py so tests can import from a path easily.
import importlib.util
import sys
from pathlib import Path

def safe_import(relative_path: str, symbol: str):
    p = Path(relative_path)
    if not p.exists():
        # Try from repo root
        p = Path.cwd() / relative_path
    spec = importlib.util.spec_from_file_location("tmp_mod", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tmp_mod"] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return getattr(mod, symbol)


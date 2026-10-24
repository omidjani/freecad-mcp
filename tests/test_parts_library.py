import importlib.util
from pathlib import Path
import sys
import types

import pytest


PARTS_LIBRARY_PATH = (
    Path(__file__).resolve().parents[1] / "addon" / "FreeCADMCP" / "rpc_server" / "parts_library.py"
)


def load_parts_library() -> types.ModuleType:
    saved = {name: sys.modules.get(name) for name in ("FreeCAD", "FreeCADGui")}
    sys.modules["FreeCAD"] = types.ModuleType("FreeCAD")
    sys.modules["FreeCADGui"] = types.ModuleType("FreeCADGui")
    try:
        spec = importlib.util.spec_from_file_location("_parts_library_test", PARTS_LIBRARY_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def test_relative_path_inside_library_is_resolved(tmp_path: Path) -> None:
    parts_library = load_parts_library()

    resolved = parts_library.resolve_library_path(str(tmp_path), "Mechanical/bolt.FCStd")

    assert resolved == str(tmp_path.resolve() / "Mechanical" / "bolt.FCStd")


@pytest.mark.parametrize("relative_path", ["../secret.FCStd", "a/../../secret.FCStd", "/etc/passwd"])
def test_paths_escaping_the_library_are_rejected(tmp_path: Path, relative_path: str) -> None:
    parts_library = load_parts_library()

    with pytest.raises(ValueError, match="outside the parts library"):
        parts_library.resolve_library_path(str(tmp_path / "lib"), relative_path)

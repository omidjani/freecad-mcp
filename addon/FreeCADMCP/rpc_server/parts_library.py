import os

import FreeCAD
import FreeCADGui


def resolve_library_path(parts_lib_path: str, relative_path: str) -> str:
    """Join ``relative_path`` onto the library root, refusing to leave it.

    ``../`` segments or an absolute path would otherwise let a caller merge
    any file on disk into the active document.
    """
    root = os.path.realpath(parts_lib_path)
    part_path = os.path.realpath(os.path.join(root, relative_path))
    if os.path.commonpath([root, part_path]) != root:
        raise ValueError(f"Path '{relative_path}' is outside the parts library.")
    return part_path


def insert_part_from_library(relative_path):
    parts_lib_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "parts_library")
    part_path = resolve_library_path(parts_lib_path, relative_path)

    if not os.path.exists(part_path):
        raise FileNotFoundError(f"Not found: {part_path}")

    # mergeProject inserts into the active document; create one if none is open
    # so we fail with a clear path instead of an AttributeError on None.
    if FreeCADGui.ActiveDocument is None:
        FreeCAD.newDocument()

    FreeCADGui.ActiveDocument.mergeProject(part_path)


def get_parts_list() -> list[str]:
    parts_lib_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "parts_library")

    if not os.path.exists(parts_lib_path):
        # Library addon not installed — return empty so the caller can show a
        # friendly "no parts found" message instead of raising over XML-RPC.
        return []

    parts = []

    for root, _, files in os.walk(parts_lib_path):
        for file in files:
            if file.endswith(".FCStd"):
                relative_path = os.path.relpath(os.path.join(root, file), parts_lib_path)
                parts.append(relative_path)

    return parts

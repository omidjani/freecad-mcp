import types

from freecad_mcp.operations import get_object_operation, list_documents_operation


def test_missing_object_reports_not_found_instead_of_null() -> None:
    freecad = types.SimpleNamespace(get_object=lambda _doc, _obj: None)

    response = get_object_operation(freecad, True, "Doc", "Ghost")

    assert len(response) == 1
    assert "Object 'Ghost' not found in document 'Doc'" in response[0].text


def test_list_documents_reports_connection_errors() -> None:
    def fail():
        raise ConnectionRefusedError("refused")

    response = list_documents_operation(types.SimpleNamespace(list_documents=fail))

    assert "Failed to list documents: refused" in response[0].text

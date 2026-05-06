"""Unit tests for the pure bulk-import parser."""

from api.utils.bulk_import import (
    MAX_BULK_IMPORT_ITEMS,
    parse_bulk_people,
)


class TestParseBulkPeople:
    def test_valid_payload_returns_models(self):
        items = [
            {"id": "p1", "name": "Alice", "email": "alice@org.example"},
            {"id": "p2", "name": "Bob", "email": "bob@org.example"},
        ]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert [p.id for p in result.valid] == ["p1", "p2"]
        assert all(p.org_id == "acme" for p in result.valid)
        assert result.errors == []
        assert result.duplicate_indexes == []

    def test_org_id_mismatch_rejected(self):
        items = [{"id": "p1", "name": "Alice", "org_id": "evil"}]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert result.valid == []
        assert len(result.errors) == 1
        assert "org_id mismatch" in result.errors[0].reason

    def test_org_id_omitted_is_filled_in(self):
        items = [{"id": "p1", "name": "Alice"}]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert result.valid[0].org_id == "acme"

    def test_validation_error_collected(self):
        items = [{"id": "p1", "name": "OK"}, {"id": "", "name": "bad"}]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert len(result.valid) == 1
        assert len(result.errors) == 1
        assert result.errors[0].index == 1

    def test_intra_payload_duplicate_id_flagged(self):
        items = [
            {"id": "dup", "name": "First"},
            {"id": "dup", "name": "Second"},
        ]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert len(result.valid) == 1
        assert result.duplicate_indexes == [1]

    def test_non_dict_row_rejected(self):
        items = ["not-an-object"]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert result.valid == []
        assert len(result.errors) == 1
        assert "object" in result.errors[0].reason

    def test_max_constant_is_1000(self):
        assert MAX_BULK_IMPORT_ITEMS == 1000

    def test_invalid_email_rejected(self):
        items = [{"id": "p1", "name": "Alice", "email": "not-an-email"}]
        result = parse_bulk_people(items, expected_org_id="acme")
        assert result.valid == []
        assert len(result.errors) == 1


def test_empty_list_returns_empty_result():
    result = parse_bulk_people([], expected_org_id="acme")
    assert result.valid == []
    assert result.errors == []
    assert result.duplicate_indexes == []

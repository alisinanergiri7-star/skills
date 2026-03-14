"""
Tests for pure utility functions in skills/pdf/scripts/extract_form_field_info.py.

These tests cover the dict-manipulation helpers that have no PDF I/O dependency.
The pypdf import at module level is mocked so these tests run without installing pypdf.
"""

import sys
import os
from unittest.mock import MagicMock

import pytest

# Mock pypdf before importing the module under test
sys.modules.setdefault("pypdf", MagicMock())

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "skills", "pdf", "scripts"),
)

from extract_form_field_info import get_full_annotation_field_id, make_field_dict


class TestGetFullAnnotationFieldId:
    """Tests for get_full_annotation_field_id — walks parent chain to build dotted ID."""

    def test_simple_field(self):
        ann = {"/T": "FirstName", "/Parent": None}
        assert get_full_annotation_field_id(ann) == "FirstName"

    def test_nested_field(self):
        parent = {"/T": "PersonalInfo", "/Parent": None}
        child = {"/T": "FirstName", "/Parent": parent}
        assert get_full_annotation_field_id(child) == "PersonalInfo.FirstName"

    def test_deeply_nested(self):
        root = {"/T": "Form", "/Parent": None}
        section = {"/T": "Section1", "/Parent": root}
        leaf = {"/T": "Field", "/Parent": section}
        assert get_full_annotation_field_id(leaf) == "Form.Section1.Field"

    def test_no_t_key_returns_none(self):
        ann = {"/Parent": None}
        assert get_full_annotation_field_id(ann) is None

    def test_none_annotation_returns_none(self):
        # Starting with None should return None
        assert get_full_annotation_field_id(None) is None

    def test_empty_dict_returns_none(self):
        assert get_full_annotation_field_id({}) is None

    def test_parent_without_t(self):
        # Parent missing /T — only child's name should appear
        parent = {"/Parent": None}
        child = {"/T": "MyField", "/Parent": parent}
        assert get_full_annotation_field_id(child) == "MyField"

    def test_uses_dict_get_interface(self):
        """Confirm it works with any dict-like object using .get()."""
        class FakeAnnot:
            def __init__(self, t, parent=None):
                self._t = t
                self._parent = parent
            def get(self, key, default=None):
                if key == "/T":
                    return self._t
                if key == "/Parent":
                    return self._parent
                return default

        parent = FakeAnnot("Group")
        child = FakeAnnot("Field", parent)
        assert get_full_annotation_field_id(child) == "Group.Field"


class TestMakeFieldDict:
    """Tests for make_field_dict — classifies PDF field types."""

    def test_text_field(self):
        field = {"/FT": "/Tx"}
        result = make_field_dict(field, "full_name")
        assert result["field_id"] == "full_name"
        assert result["type"] == "text"

    def test_checkbox_with_off_state(self):
        field = {"/FT": "/Btn", "/_States_": ["/Yes", "/Off"]}
        result = make_field_dict(field, "agree")
        assert result["type"] == "checkbox"
        assert result["checked_value"] == "/Yes"
        assert result["unchecked_value"] == "/Off"

    def test_checkbox_off_first(self):
        field = {"/FT": "/Btn", "/_States_": ["/Off", "/Yes"]}
        result = make_field_dict(field, "agree")
        assert result["checked_value"] == "/Yes"
        assert result["unchecked_value"] == "/Off"

    def test_checkbox_no_off_state(self, capsys):
        field = {"/FT": "/Btn", "/_States_": ["/A", "/B"]}
        result = make_field_dict(field, "choice_box")
        assert result["type"] == "checkbox"
        assert result["checked_value"] == "/A"
        assert result["unchecked_value"] == "/B"
        # Should print a warning
        captured = capsys.readouterr()
        assert "choice_box" in captured.out or "Unexpected" in captured.out

    def test_checkbox_no_states(self):
        field = {"/FT": "/Btn", "/_States_": []}
        result = make_field_dict(field, "lone_btn")
        assert result["type"] == "checkbox"
        assert "checked_value" not in result

    def test_choice_field(self):
        field = {
            "/FT": "/Ch",
            "/_States_": [("us", "United States"), ("ca", "Canada")],
        }
        result = make_field_dict(field, "country")
        assert result["type"] == "choice"
        assert len(result["choice_options"]) == 2
        assert result["choice_options"][0] == {"value": "us", "text": "United States"}
        assert result["choice_options"][1] == {"value": "ca", "text": "Canada"}

    def test_choice_field_empty_options(self):
        field = {"/FT": "/Ch", "/_States_": []}
        result = make_field_dict(field, "empty_choice")
        assert result["type"] == "choice"
        assert result["choice_options"] == []

    def test_unknown_field_type(self):
        field = {"/FT": "/Sig"}
        result = make_field_dict(field, "signature")
        assert result["type"] == "unknown (/Sig)"

    def test_missing_ft_key(self):
        field = {}
        result = make_field_dict(field, "mystery")
        assert result["field_id"] == "mystery"
        assert "unknown" in result["type"]
        assert "None" in result["type"]

    def test_field_id_preserved(self):
        field = {"/FT": "/Tx"}
        result = make_field_dict(field, "section1.name")
        assert result["field_id"] == "section1.name"

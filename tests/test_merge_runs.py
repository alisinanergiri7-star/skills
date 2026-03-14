"""
Tests for pure helper functions in skills/docx/scripts/office/helpers/merge_runs.py.

These tests work directly with xml.dom.minidom (stdlib) and mock defusedxml
so no extra packages are required for the pure-logic helpers.
The file-I/O entrypoint (merge_runs) is tested separately with a real temp directory.
"""

import sys
import os
import xml.dom.minidom as minidom
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# defusedxml is not always installed; mock it so the module imports cleanly
_defusedxml_mock = MagicMock()
_defusedxml_mock.minidom = MagicMock()
sys.modules.setdefault("defusedxml", _defusedxml_mock)
sys.modules.setdefault("defusedxml.minidom", _defusedxml_mock.minidom)

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "skills", "docx", "scripts", "office", "helpers"
    ),
)

from merge_runs import (
    _find_elements,
    _get_child,
    _get_children,
    _is_adjacent,
    _is_run,
    _can_merge,
    _next_element_sibling,
)


# ---------------------------------------------------------------------------
# Helpers to build minidom fragments
# ---------------------------------------------------------------------------

def make_doc(xml_str: str):
    return minidom.parseString(xml_str)


def para_with_runs(*run_contents):
    """Build a <w:p> with one <w:r><w:t>text</w:t></w:r> per arg."""
    parts = []
    for text in run_contents:
        parts.append(f"<w:r><w:t>{text}</w:t></w:r>")
    return make_doc(f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{"".join(parts)}</w:p>')


def run_with_rpr(props_xml: str, text: str):
    return f"<w:r><w:rPr>{props_xml}</w:rPr><w:t>{text}</w:t></w:r>"


# ---------------------------------------------------------------------------
# _find_elements
# ---------------------------------------------------------------------------

class TestFindElements:
    def test_finds_direct_children(self):
        doc = make_doc("<root><r/><r/><p/></root>")
        root = doc.documentElement
        found = _find_elements(root, "r")
        assert len(found) == 2

    def test_finds_nested_elements(self):
        doc = make_doc("<root><p><r/></p><r/></root>")
        root = doc.documentElement
        found = _find_elements(root, "r")
        assert len(found) == 2

    def test_finds_namespaced_elements(self):
        doc = para_with_runs("hello", "world")
        root = doc.documentElement
        found = _find_elements(root, "r")
        assert len(found) == 2

    def test_returns_empty_when_not_found(self):
        doc = make_doc("<root><p/></root>")
        found = _find_elements(doc.documentElement, "r")
        assert found == []

    def test_returns_all_matching_tags(self):
        doc = make_doc("<root><a/><b/><a/><c><a/></c></root>")
        found = _find_elements(doc.documentElement, "a")
        assert len(found) == 3


# ---------------------------------------------------------------------------
# _get_child / _get_children
# ---------------------------------------------------------------------------

class TestGetChild:
    def test_returns_first_matching_child(self):
        doc = make_doc("<root><rPr/><t>hi</t></root>")
        root = doc.documentElement
        child = _get_child(root, "rPr")
        assert child is not None
        assert (child.localName or child.tagName) in ("rPr", "w:rPr")

    def test_returns_none_when_absent(self):
        doc = make_doc("<root><t>hi</t></root>")
        assert _get_child(doc.documentElement, "rPr") is None

    def test_only_direct_children(self):
        doc = make_doc("<root><wrapper><rPr/></wrapper></root>")
        # rPr is not a direct child of root
        assert _get_child(doc.documentElement, "rPr") is None


class TestGetChildren:
    def test_returns_all_matching_children(self):
        doc = make_doc("<root><t>a</t><t>b</t><rPr/></root>")
        children = _get_children(doc.documentElement, "t")
        assert len(children) == 2

    def test_returns_empty_list_when_absent(self):
        doc = make_doc("<root><rPr/></root>")
        assert _get_children(doc.documentElement, "t") == []


# ---------------------------------------------------------------------------
# _is_run
# ---------------------------------------------------------------------------

class TestIsRun:
    def test_plain_run_element(self):
        doc = make_doc("<r/>")
        assert _is_run(doc.documentElement)

    def test_namespaced_run_element(self):
        doc = para_with_runs("text")
        root = doc.documentElement
        runs = _find_elements(root, "r")
        assert all(_is_run(r) for r in runs)

    def test_non_run_element(self):
        doc = make_doc("<p/>")
        assert not _is_run(doc.documentElement)

    def test_rpr_is_not_run(self):
        doc = make_doc("<rPr/>")
        assert not _is_run(doc.documentElement)


# ---------------------------------------------------------------------------
# _is_adjacent
# ---------------------------------------------------------------------------

class TestIsAdjacent:
    def test_immediately_adjacent(self):
        doc = make_doc("<p><r id='1'/><r id='2'/></p>")
        children = [
            c for c in doc.documentElement.childNodes
            if c.nodeType == c.ELEMENT_NODE
        ]
        assert _is_adjacent(children[0], children[1])

    def test_not_adjacent_with_element_in_between(self):
        doc = make_doc("<p><r id='1'/><x/><r id='2'/></p>")
        children = [
            c for c in doc.documentElement.childNodes
            if c.nodeType == c.ELEMENT_NODE
        ]
        assert not _is_adjacent(children[0], children[2])

    def test_not_adjacent_reversed(self):
        doc = make_doc("<p><r id='1'/><r id='2'/></p>")
        children = [
            c for c in doc.documentElement.childNodes
            if c.nodeType == c.ELEMENT_NODE
        ]
        # elem2 before elem1 — should not be adjacent in forward direction
        assert not _is_adjacent(children[1], children[0])


# ---------------------------------------------------------------------------
# _next_element_sibling
# ---------------------------------------------------------------------------

class TestNextElementSibling:
    def test_returns_next_element(self):
        doc = make_doc("<p><r/><t/></p>")
        children = [
            c for c in doc.documentElement.childNodes
            if c.nodeType == c.ELEMENT_NODE
        ]
        nxt = _next_element_sibling(children[0])
        assert nxt is children[1]

    def test_returns_none_at_end(self):
        doc = make_doc("<p><r/></p>")
        child = next(
            c for c in doc.documentElement.childNodes
            if c.nodeType == c.ELEMENT_NODE
        )
        assert _next_element_sibling(child) is None


# ---------------------------------------------------------------------------
# _can_merge
# ---------------------------------------------------------------------------

class TestCanMerge:
    def _make_run(self, rpr_xml: str | None, text: str = "x") -> minidom.Element:
        if rpr_xml:
            xml_str = f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr>{rpr_xml}</w:rPr><w:t>{text}</w:t></w:r>'
        else:
            xml_str = f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:t>{text}</w:t></w:r>'
        return minidom.parseString(xml_str).documentElement

    def test_both_no_rpr_can_merge(self):
        r1 = self._make_run(None, "hello")
        r2 = self._make_run(None, " world")
        assert _can_merge(r1, r2)

    def test_identical_rpr_can_merge(self):
        rpr = "<w:b/>"
        r1 = self._make_run(rpr, "hello")
        r2 = self._make_run(rpr, " world")
        assert _can_merge(r1, r2)

    def test_different_rpr_cannot_merge(self):
        r1 = self._make_run("<w:b/>", "bold")
        r2 = self._make_run("<w:i/>", "italic")
        assert not _can_merge(r1, r2)

    def test_one_has_rpr_other_does_not(self):
        r1 = self._make_run("<w:b/>", "bold")
        r2 = self._make_run(None, "plain")
        assert not _can_merge(r1, r2)

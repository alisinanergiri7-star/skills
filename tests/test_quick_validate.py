"""
Tests for skills/skill-creator/scripts/quick_validate.py

Covers:
- Valid skill passes validation
- Missing SKILL.md
- Missing frontmatter
- Invalid YAML
- Missing required fields (name, description)
- Invalid name format (non-kebab-case)
- Name too long (> 64 chars)
- Description too long (> 1024 chars)
- Description with angle brackets
- Unexpected frontmatter keys
- License referencing missing LICENSE.txt
- Compatibility field validation
"""

import sys
import os
import tempfile
import textwrap
from pathlib import Path

import pytest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "skills", "skill-creator", "scripts"),
)

from quick_validate import validate_skill


def make_skill(tmp_path: Path, content: str) -> Path:
    """Write a SKILL.md to a temporary directory and return the dir."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(content)
    return skill_dir


MINIMAL_VALID = textwrap.dedent("""\
    ---
    name: my-skill
    description: A skill that does something useful when you ask it.
    ---

    ## Instructions
    Do the thing.
""")


class TestValidSkill:
    def test_minimal_valid_skill(self, tmp_path):
        skill_dir = make_skill(tmp_path, MINIMAL_VALID)
        valid, msg = validate_skill(skill_dir)
        assert valid is True
        assert "valid" in msg.lower()

    def test_skill_with_license_field(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: licensed-skill
            description: Does something.
            license: Apache 2.0
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, _ = validate_skill(skill_dir)
        assert valid is True

    def test_skill_with_all_allowed_fields(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: full-skill
            description: A complete skill with all optional fields.
            license: Apache 2.0
            compatibility: bash
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, _ = validate_skill(skill_dir)
        assert valid is True

    def test_name_with_digits(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: skill-v2
            description: Version 2 of the skill.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, _ = validate_skill(skill_dir)
        assert valid is True


class TestMissingOrBadFile:
    def test_missing_skill_md(self, tmp_path):
        skill_dir = tmp_path / "empty-skill"
        skill_dir.mkdir()
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "SKILL.md" in msg

    def test_no_frontmatter(self, tmp_path):
        skill_dir = make_skill(tmp_path, "# Just a markdown file\nNo frontmatter here.")
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "frontmatter" in msg.lower()

    def test_unclosed_frontmatter(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: broken-skill
            description: Missing closing fence
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False

    def test_invalid_yaml_frontmatter(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: [unclosed bracket
            description: bad yaml
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "YAML" in msg or "yaml" in msg.lower()


class TestRequiredFields:
    def test_missing_name(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            description: A skill without a name.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "name" in msg.lower()

    def test_missing_description(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: no-description
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "description" in msg.lower()


class TestNameValidation:
    def test_name_with_uppercase(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: MySkill
            description: Has uppercase.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "kebab" in msg.lower() or "lowercase" in msg.lower()

    def test_name_with_spaces(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: my skill
            description: Has spaces.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False

    def test_name_with_underscore(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: my_skill
            description: Has underscore.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False

    def test_name_starts_with_hyphen(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: -bad-name
            description: Starts with hyphen.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False

    def test_name_ends_with_hyphen(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: bad-name-
            description: Ends with hyphen.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False

    def test_name_consecutive_hyphens(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: bad--name
            description: Has consecutive hyphens.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False

    def test_name_too_long(self, tmp_path):
        long_name = "a" * 65
        content = textwrap.dedent(f"""\
            ---
            name: {long_name}
            description: Name exceeds 64 characters.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "64" in msg or "long" in msg.lower()

    def test_name_exactly_64_chars(self, tmp_path):
        name = "a" * 64
        content = textwrap.dedent(f"""\
            ---
            name: {name}
            description: Name is exactly 64 characters.
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, _ = validate_skill(skill_dir)
        assert valid is True


class TestDescriptionValidation:
    def test_description_too_long(self, tmp_path):
        long_desc = "A" * 1025
        content = textwrap.dedent(f"""\
            ---
            name: my-skill
            description: "{long_desc}"
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "1024" in msg or "long" in msg.lower()

    def test_description_exactly_1024_chars(self, tmp_path):
        desc = "A" * 1024
        content = f'---\nname: my-skill\ndescription: "{desc}"\n---\n'
        skill_dir = make_skill(tmp_path, content)
        valid, _ = validate_skill(skill_dir)
        assert valid is True

    def test_description_with_angle_brackets(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: my-skill
            description: "Triggered when user types <command>"
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "angle" in msg.lower() or "<" in msg or ">" in msg


class TestUnexpectedKeys:
    def test_unexpected_frontmatter_key(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: my-skill
            description: Valid description.
            author: someone
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "author" in msg or "unexpected" in msg.lower()


class TestLicenseValidation:
    def test_license_referencing_missing_file(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: my-skill
            description: Uses a proprietary license.
            license: "Complete terms in LICENSE.txt"
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        valid, msg = validate_skill(skill_dir)
        assert valid is False
        assert "LICENSE.txt" in msg

    def test_license_with_existing_file(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            name: my-skill
            description: Has a license file.
            license: "Complete terms in LICENSE.txt"
            ---
        """)
        skill_dir = make_skill(tmp_path, content)
        (skill_dir / "LICENSE.txt").write_text("Apache 2.0")
        valid, _ = validate_skill(skill_dir)
        assert valid is True

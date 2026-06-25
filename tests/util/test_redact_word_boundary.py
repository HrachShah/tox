"""Regression tests for ``tox.util.redact`` keyword boundary detection."""

from __future__ import annotations

import pytest

from tox.util.redact import redact_argv, redact_value


@pytest.mark.parametrize(
    ("name", "do_redact"),
    [
        # Substring matches that previously triggered false positives:
        pytest.param("KEYBOARD_LAYOUT", False, id="keyboard_layout_substring"),
        pytest.param("TOKENIZER", False, id="tokenizer_substring"),
        pytest.param("AUTHORITY", False, id="authority_substring"),
        pytest.param("AUTHORS", False, id="authors_substring"),
        pytest.param("CLIENT_VERSION", True, id="client_version_substring"),
        pytest.param("CREDENTIALS_FILE", False, id="credentials_substring"),
        pytest.param("ACCESSIBILITY", False, id="accessibility_substring"),
        pytest.param("MY_API_KEY_FALLBACK", True, id="api_key_with_suffix"),
        pytest.param("PREMIUM", False, id="unrelated_word"),
        pytest.param("PATH", False, id="path"),
        # Word-boundary matches that should still redact:
        pytest.param("MY_KEY", True, id="my_key_underscore"),
        pytest.param("GITHUB_TOKEN", True, id="github_token_underscore"),
        pytest.param("API-KEY", True, id="api_key_dash"),
        pytest.param("DB.PASSWORD", True, id="db_password_dot"),
        pytest.param("KEY", True, id="key_alone"),
    ],
)
def test_redact_value_word_boundary(name: str, do_redact: bool) -> None:
    result = redact_value(name, "foo")
    if do_redact:
        assert result == "***"
    else:
        assert result == "foo"


def test_redact_argv_keyboard_layout_not_redacted() -> None:
    """A flag named ``--keyboard-layout`` does not look like a secret."""
    result = redact_argv(["--keyboard-layout=us"])
    assert result == ["--keyboard-layout=us"]


def test_redact_argv_keyword_anywhere_in_name() -> None:
    """A keyword anywhere in the flag name (not just at the start) is redacted."""
    result = redact_argv(["--my-prefix-token=ghp_abcdef"])
    assert result == ["--my-prefix-token=**********"]


def test_redact_argv_tokenize_not_redacted() -> None:
    """``--tokenize`` is a real flag (e.g. spacy), not a token flag."""
    result = redact_argv(["spacy", "--tokenize=true"])
    assert result == ["spacy", "--tokenize=true"]

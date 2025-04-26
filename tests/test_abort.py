"""
Tests for the AbortChange exception.
"""

import pytest

from upd8 import AbortChange, Versioned, changes


class ExceptionTest(Versioned):
    """Test class for AbortChange exception"""

    @changes
    def raise_abort(self):
        raise AbortChange("Return this")

    @changes
    def conditional_abort(self, condition):
        if condition:
            raise AbortChange("Aborted")
        return "No abort"


def test_abort_update_is_exception():
    """Test that AbortChange is a proper exception"""
    assert issubclass(AbortChange, Exception)


def test_abort_update_can_be_raised():
    """Test that AbortChange can be raised and caught"""
    with pytest.raises(AbortChange):
        raise AbortChange()


def test_abort_in_changes_method():
    """Test that AbortChange in a @changes method is suppressed and prevents version increment"""
    obj = ExceptionTest()
    initial_version = obj.version

    # Should return the raised value
    result = obj.raise_abort()
    assert result == "Return this"

    # Version should not have been incremented
    assert obj.version == initial_version


def test_conditional_abort():
    """Test conditional abort based on a parameter"""
    obj = ExceptionTest()
    initial_version = obj.version

    # Should abort but not raise exception, and not increment version
    result = obj.conditional_abort(True)
    assert result == "Aborted"
    assert obj.version == initial_version

    # Should not abort and should increment version
    result = obj.conditional_abort(False)
    assert result == "No abort"
    assert obj.version == initial_version + 1


def test_abort_caught_in_context_manager():
    """Test that AbortChange is suppressed when raised within a context manager"""
    obj = ExceptionTest()
    initial_version = obj.version

    # Context manager should suppress AbortChange exception
    with obj.change:
        raise AbortChange()  # This should be caught by the context manager

    # Should reach here without exception
    # Version should not increment
    assert obj.version == initial_version

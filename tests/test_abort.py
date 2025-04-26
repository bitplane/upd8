"""
Tests for the AbortUpdate exception.
"""

import pytest

from upd8 import AbortUpdate, Versioned, changes


class ExceptionTest(Versioned):
    """Test class for AbortUpdate exception"""

    @changes
    def raise_abort(self):
        raise AbortUpdate()
        return "Shouldn't reach here"

    @changes
    def conditional_abort(self, condition):
        if condition:
            raise AbortUpdate()
        return "No abort"


def test_abort_update_is_exception():
    """Test that AbortUpdate is a proper exception"""
    assert issubclass(AbortUpdate, Exception)


def test_abort_update_can_be_raised():
    """Test that AbortUpdate can be raised and caught"""
    with pytest.raises(AbortUpdate):
        raise AbortUpdate()


def test_abort_in_changes_method():
    """Test that AbortUpdate in a @changes method is suppressed and prevents version increment"""
    obj = ExceptionTest()
    initial_version = obj.version

    # Should not raise, but should return None
    result = obj.raise_abort()
    assert result is None

    # Version should not have been incremented
    assert obj.version == initial_version


def test_conditional_abort():
    """Test conditional abort based on a parameter"""
    obj = ExceptionTest()
    initial_version = obj.version

    # Should abort but not raise exception, and not increment version
    result = obj.conditional_abort(True)
    assert result is None
    assert obj.version == initial_version

    # Should not abort and should increment version
    result = obj.conditional_abort(False)
    assert result == "No abort"
    assert (
        obj.version == initial_version + 1
    )  # Version incremented for successful execution


def test_abort_suppression_in_context_manager():
    """Test that AbortUpdate is suppressed when raised within a context manager"""
    obj = ExceptionTest()
    initial_version = obj.version

    # Context manager should suppress AbortUpdate exception
    with obj.change:
        raise AbortUpdate()  # This should be caught by the context manager

    # Should reach here without exception
    # Version should not increment
    assert obj.version == initial_version

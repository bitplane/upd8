"""
Tests for the Versioned base class.
"""

from upd8 import AbortChange, Versioned, field


class SimpleVersioned(Versioned):
    """Test class for Versioned"""

    value = field(0)


def test_init():
    """Test that Versioned initializes correctly"""
    obj = Versioned()
    assert obj.version == 0
    assert hasattr(obj, "change")


def test_change_method():
    """Test the change method increments version"""
    obj = Versioned()
    old_version = obj.version
    obj.change()
    assert obj.version == old_version + 1


def test_change_context():
    """Test the change context manager increments version once"""
    obj = SimpleVersioned()
    old_version = obj.version

    with obj.change:
        pass  # Empty context manager

    # Version should increment by 1
    assert obj.version == old_version + 1


def test_field_change_increments_version():
    """Test that changing a field increments version"""
    obj = SimpleVersioned()
    old_version = obj.version
    obj.value = 1
    assert obj.version == old_version + 1


def test_no_increment_if_value_unchanged():
    """Test that setting the same value doesn't increment version"""
    obj = SimpleVersioned()
    obj.value = 1
    old_version = obj.version
    obj.value = 1  # Same value
    assert obj.version == old_version  # No change


def test_hash():
    """Test object hash changes when version changes"""
    obj = SimpleVersioned()
    hash1 = hash(obj)
    obj.change()
    hash2 = hash(obj)
    assert hash1 != hash2


def test_inequality():
    """Test inequality based on identity and version"""
    obj1 = SimpleVersioned()
    obj2 = SimpleVersioned()

    # Different objects should not be equal
    assert obj1 != obj2


def test_inequality_by_type():
    """Test equality based on identity and version"""
    obj1 = SimpleVersioned()
    obj2 = object()

    # Different objects should not be equal
    assert obj1 != obj2


def test_equality():
    """Test equality based on identity and version"""
    obj1 = SimpleVersioned()
    obj2 = obj1

    assert obj1 == obj2


def test_abort_in_context():
    """Test that AbortChange in a context doesn't increment version"""
    obj = SimpleVersioned()
    old_version = obj.version

    # First, let's verify that a normal context increments the version by 1
    with obj.change:
        pass  # Empty context

    assert obj.version == old_version + 1
    current_version = obj.version

    # Now test with abort
    with obj.change:
        raise AbortChange()  # Should be suppressed

    # The version shouldn't change from the previous value
    assert obj.version == current_version

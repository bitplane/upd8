"""
Tests for the decorators.
"""

from upd8 import AbortChange, Versioned, changes, field, waits


class DecoratorTest(Versioned):
    """Test class for decorators"""

    value = field(0)

    @changes
    def increment(self, amount=1):
        self.value += amount
        return self.value

    @waits
    def get_value(self):
        return self.value

    @changes
    def abort_if_negative(self, value):
        if value < 0:
            raise AbortChange()
        self.value = value
        return True


def test_changes_decorator():
    """Test that @changes decorator increments version"""
    obj = DecoratorTest()
    old_version = obj.version

    result = obj.increment()

    assert result == 1  # Method returns the new value
    assert obj.value == 1  # Value is updated
    assert obj.version > old_version  # Version is incremented


def test_waits_decorator():
    """Test that @waits decorator doesn't increment version"""
    obj = DecoratorTest()
    obj.value = 42
    old_version = obj.version

    result = obj.get_value()

    assert result == 42  # Method returns the current value
    assert obj.version == old_version  # Version is not incremented


def test_changes_abort_update():
    """Test that AbortChange in @changes method is properly handled"""
    obj = DecoratorTest()
    old_version = obj.version
    old_value = obj.value

    result = obj.abort_if_negative(-1)

    assert result is None  # Should return None when aborted
    assert obj.value == old_value  # Value shouldn't change
    assert obj.version == old_version  # Version shouldn't increment

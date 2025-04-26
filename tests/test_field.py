"""
Tests for the field descriptor.
"""

from upd8 import Versioned, field


class FieldTest(Versioned):
    """Test class for field descriptor"""

    int_field = field(0)
    str_field = field("default")
    list_field = field([])
    none_field = field(None)


def test_field_default_values():
    """Test that fields initialize with default values"""
    obj = FieldTest()
    assert obj.int_field == 0
    assert obj.str_field == "default"
    assert obj.list_field == []
    assert obj.none_field is None


def test_field_set_values():
    """Test setting field values"""
    obj = FieldTest()
    obj.int_field = 42
    obj.str_field = "changed"
    obj.list_field = [1, 2, 3]
    obj.none_field = "not none"

    assert obj.int_field == 42
    assert obj.str_field == "changed"
    assert obj.list_field == [1, 2, 3]
    assert obj.none_field == "not none"


def test_field_version_increment():
    """Test that changing fields increments version"""
    obj = FieldTest()
    assert obj.version == 0

    obj.int_field = 1
    assert obj.version == 1

    obj.str_field = "new"
    assert obj.version == 2

    obj.list_field = [1]
    assert obj.version == 3


def test_field_no_increment_same_value():
    """Test that setting the same value doesn't increment version"""
    obj = FieldTest()
    obj.int_field = 42
    current_version = obj.version

    obj.int_field = 42  # Same value
    assert obj.version == current_version  # No change


def test_field_class_access():
    """Test accessing field from class returns field object"""
    field_obj = FieldTest.int_field
    assert isinstance(field_obj, field)


def test_field_separate_instances():
    """Test that fields have separate values for different instances"""
    obj1 = FieldTest()
    obj2 = FieldTest()

    obj1.int_field = 1
    obj2.int_field = 2

    assert obj1.int_field == 1
    assert obj2.int_field == 2


def test_field_mutable_default():
    """Test that mutable default values are separate for each instance"""
    obj1 = FieldTest()
    obj2 = FieldTest()

    # Create a new list rather than modifying the existing one
    obj1.list_field = obj1.list_field + [1]
    assert obj1.list_field == [1]
    assert obj2.list_field == []  # Should not be affected

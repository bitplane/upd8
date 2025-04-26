"""
Field descriptor for Versioned classes.
"""

from typing import Generic, TypeVar

T = TypeVar("T")


class field(Generic[T]):
    """
    Declarative versioned field with a default value.

    Example:
        class Counter(Versioned):
            count: int = field(0)
            name: str = field("default")
    """

    def __init__(self, default_value: T):
        self.default_value = default_value
        self.name = None  # Will be set during __set_name__

    def __set_name__(self, owner, name):
        self.name = name
        # Create private attribute name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None) -> T:
        if obj is None:
            return self

        lock = getattr(obj, "_Versioned__lock")
        with lock:
            # Initialize if not already set
            if not hasattr(obj, self.private_name):
                setattr(obj, self.private_name, self.default_value)

            return getattr(obj, self.private_name)

    def __set__(self, obj, value: T) -> None:
        lock = getattr(obj, "_Versioned__lock")
        with lock:
            # Only increment version if value changed
            old_value = getattr(obj, self.private_name, None)
            if old_value != value:
                setattr(obj, self.private_name, value)
                obj._version += 1

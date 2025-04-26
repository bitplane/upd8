"""
Base class for objects with versioning and thread-safe access.
"""

import threading
from typing import Any

from upd8._exception import AbortUpdate


class _Change:
    """
    Helper class that provides both method call and context manager functionality
    for version tracking. Supports both synchronous and asynchronous contexts.
    """

    def __init__(self, versioned):
        self.versioned = versioned

    def __call__(self):
        """Called when used as a method"""
        with self.versioned._Versioned__lock:
            self.versioned._version += 1
        return self.versioned

    def __enter__(self):
        """Called when used as a synchronous context manager"""
        self.versioned._Versioned__lock.acquire()
        return self.versioned

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the synchronous context"""
        try:
            if exc_type is not AbortUpdate:
                self.versioned._version += 1
        finally:
            self.versioned._Versioned__lock.release()
        return exc_type is AbortUpdate  # Suppress AbortUpdate exceptions

    async def __aenter__(self):
        """Called when used as an asynchronous context manager"""
        self.versioned._Versioned__lock.acquire()
        return self.versioned

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the asynchronous context"""
        try:
            if exc_type is not AbortUpdate:
                self.versioned._version += 1
        finally:
            self.versioned._Versioned__lock.release()
        return exc_type is AbortUpdate  # Suppress AbortUpdate exceptions


class Versioned:
    """
    Base class for objects whose state changes should be trackable via a version number.
    Includes a reentrant lock for thread safety when modifying or accessing state.
    """

    def __init__(self):
        """Initializes version to 0 and creates a reentrant lock."""
        self._version: int = 0
        # Use RLock for reentrancy: no deadlocks if entered twice by the same thread
        # Use name mangling (__lock) to avoid conflicts with subclasses
        self.__lock: threading.RLock = threading.RLock()
        # Create a change object that works both as method and context manager
        self.change = _Change(self)

    @property
    def version(self) -> int:
        """
        Returns the current version number of this object.
        """
        with self.__lock:
            return self._version

    def __hash__(self) -> int:
        """
        Makes Versioned objects hashable based on identity and current version.
        Useful for caching mechanisms that depend on object state.
        """
        with self.__lock:
            return hash((id(self), self._version))

    def __eq__(self, other: Any) -> bool:
        """
        Equality check based on identity and version.
        Two Versioned objects are equal if they are the same object instance
        and have the same version number.
        """
        if not isinstance(other, Versioned):
            return False

        # Need to acquire both locks to prevent race conditions
        # Use a consistent locking order to prevent deadlocks
        self_id, other_id = id(self), id(other)
        first, second = (self, other) if self_id < other_id else (other, self)

        # Access the mangled lock attribute - always use "Versioned" as the class name
        # because that's where __lock is defined
        first_lock = getattr(first, "_Versioned__lock")
        second_lock = getattr(second, "_Versioned__lock")

        with first_lock:
            with second_lock:
                return (self_id == other_id) and (self._version == other._version)

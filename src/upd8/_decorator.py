"""
Decorators for Versioned objects.
"""

import inspect
from functools import wraps

from upd8._exception import AbortUpdate
from upd8._versioned import Versioned


def changes(method):
    """
    Decorate state mutating methods with this.
    Works with both synchronous and asynchronous methods.
    Automatically uses the change context manager.

    If a method raises AbortUpdate, the exception is caught and the method
    returns None without incrementing the version.
    """

    @wraps(method)
    def sync_wrapper(self: Versioned, *args, **kwargs):
        # For synchronous methods
        try:
            with self.change:
                return method(self, *args, **kwargs)
        except AbortUpdate:
            return None  # Suppress AbortUpdate exception

    @wraps(method)
    async def async_wrapper(self: Versioned, *args, **kwargs):
        # For asynchronous methods
        try:
            async with self.change:
                return await method(self, *args, **kwargs)
        except AbortUpdate:
            return None  # Suppress AbortUpdate exception

    # Check if the method is asynchronous and return the appropriate wrapper
    if inspect.iscoroutinefunction(method):
        return async_wrapper
    else:
        return sync_wrapper


def waits(method):
    """
    Decorate state awaiting methods with this.
    Works with both synchronous and asynchronous methods.
    Automatically acquires the lock for thread-safe access.
    """

    @wraps(method)
    def sync_wrapper(self: Versioned, *args, **kwargs):
        # For synchronous methods
        lock = getattr(self, "_Versioned__lock")
        with lock:
            result = method(self, *args, **kwargs)
        return result

    @wraps(method)
    async def async_wrapper(self: Versioned, *args, **kwargs):
        # For asynchronous methods
        lock = getattr(self, "_Versioned__lock")
        with lock:
            result = await method(self, *args, **kwargs)
        return result

    # Check if the method is asynchronous and return the appropriate wrapper
    if inspect.iscoroutinefunction(method):
        return async_wrapper
    else:
        return sync_wrapper

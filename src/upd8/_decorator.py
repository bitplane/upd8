"""
Decorators for Versioned objects.
"""

import inspect
from functools import wraps

from upd8._exception import AbortChange
from upd8._versioned import Versioned


def changes(method):
    """
    Decorate state mutating methods with this.
    Works with both synchronous and asynchronous methods.
    Automatically uses the change context manager.

    If a method raises AbortChange, the exception is caught and the method
    returns the return value passed to the exception.
    """

    @wraps(method)
    def sync_wrapper(self: Versioned, *args, **kwargs):
        # For synchronous methods
        try:
            with self._Versioned__lock:
                result = method(self, *args, **kwargs)
                self.change()
                return result
        except AbortChange as abort:
            return abort.return_value

    @wraps(method)
    async def async_wrapper(self: Versioned, *args, **kwargs):
        # For asynchronous methods
        try:
            with self._Versioned__lock:
                result = await method(self, *args, **kwargs)
                self.change()
                return result
        except AbortChange as abort:
            return abort.return_value

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
        with self._Versioned__lock:
            result = method(self, *args, **kwargs)
        return result

    @wraps(method)
    async def async_wrapper(self: Versioned, *args, **kwargs):
        # For asynchronous methods
        with self._Versioned__lock:
            result = await method(self, *args, **kwargs)
        return result

    # Check if the method is asynchronous and return the appropriate wrapper
    if inspect.iscoroutinefunction(method):
        return async_wrapper
    else:
        return sync_wrapper

"""
Helper for applying changes in a context manager or the update method
"""

from upd8._exception import AbortChange


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
            return self.versioned.version

    def __enter__(self):
        """Called when used as a synchronous context manager"""
        self.versioned._Versioned__lock.acquire()
        return self.versioned

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the synchronous context"""
        try:
            if exc_type is not AbortChange:
                self.versioned._version += 1
        finally:
            self.versioned._Versioned__lock.release()
        return exc_type is AbortChange

    async def __aenter__(self):
        """Called when used as an asynchronous context manager"""
        self.versioned._Versioned__lock.acquire()
        return self.versioned

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the asynchronous context"""
        try:
            if exc_type is not AbortChange:
                self.versioned._version += 1
        finally:
            self.versioned._Versioned__lock.release()
        return exc_type is AbortChange

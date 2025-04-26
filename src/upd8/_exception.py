"""
Exception classes for the upd8 package.
"""


class AbortChange(Exception):
    """
    Raise this exception to exit a @changes decorated method
    without incrementing the version.

    Can optionally include a return value.
    """

    def __init__(self, return_value=None):
        self.return_value = return_value
        super().__init__()

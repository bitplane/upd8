"""
Exception classes for the upd8 package.
"""


class AbortUpdate(Exception):
    """
    Raise this exception if you want to exit a @changes decorated method
    without incrementing the version.
    """

    pass

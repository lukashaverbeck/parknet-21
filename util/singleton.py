from typing import Optional


class Singleton:
    """ Decorator ensuring that there can be only one instance of a class within memory space.

    Whenever a class decorated with ``@Singleton`` is called, the same instance of the class is returned.
    For retrieving an instance of a ``Singleton`` class, the usual syntax for creating objects can be used.

    Notes:
        This class is intended to be used as a class decorator.

    Attributes:
        cls: decorated class
        instance: instance of the decorated class that is used whenever such an instance is requested
    """

    def __init__(self, cls: type):
        self.cls: type = cls
        self.instance: Optional[object] = None

    def __call__(self, *args, **kwargs):
        # create an instance if there is none already
        if self.instance is None:
            self.instance = self.cls(*args, **kwargs)

        return self.instance

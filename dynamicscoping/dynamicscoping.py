#!/usr/bin/env python
# coding: utf-8


"""Mimic dynamic binding with context managers."""


import threading
from contextlib import contextmanager


#
# Business
#


class UninitializedBinding(ValueError):
    """Uninitialized value for a dynamically bound object."""


class DynamicVar(object):
    """
    A variable which can be bound to a value within a context.

    Don't instantiate this directly: use ``dynamically_bound()``.
    """

    def __init__(self, initial=UninitializedBinding, name=None):
        """Initialize a dynamically bound variable."""
        self._root_thread = threading.current_thread()
        self._local = threading.local()
        self._name = name or id(self)
        self._set(initial)

    def __repr__(self):
        """Represent a dynamic variable."""
        if self._name == id(self):
            return '<{} ({}) = {}>'.format(
                self.__class__.__name__,
                id(self),
                self._value,
            )
        else:
            return '<{} "{}" ({}) = {}>'.format(
                self.__class__.__name__,
                self._name,
                id(self),
                self._value,
            )

    @contextmanager
    def binding(self, value):
        """Set a dynamic variable's value within the context."""
        old_value = self._value
        self._set(value)
        yield
        self._set(old_value)

    def _set(self, value):
        """Set the variable, handling the root thread specially."""
        self._local._value = value
        if threading.current_thread() is self._root_thread:
            self._root_value = value

    @property
    def _value(self):
        """Get the value of our variable."""
        # If we have not been initialized, it means we're in a thread: take the
        # value from the root thread.
        if not hasattr(self._local, '_value'):
            self._local._value = self._root_value
        return self._local._value

    @property
    def value(self):
        """Get the value of this variable."""
        if self.is_bound():
            return self._value
        else:
            raise UninitializedBinding('{} is unbound.'.format(self))

    def is_bound(self):
        """Check if we've been bound or not."""
        if self._value is UninitializedBinding:
            return False
        else:
            return True


def dynamically_bound(*args, **kwargs):
    """Create a dynamic variable."""
    return DynamicVar(*args, **kwargs)

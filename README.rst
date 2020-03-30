Emulate Dynamic Scoping with Context Managers
===============================================================================

This library allows you to pass information deep into a call stack as if you
were using a global variable, but avoiding most of the usual global variable
pitfalls.


Motivation
----------

Consider a situation where you want to convey information deep into the call
stack.  For example, say we want to control logging in some deep function::

    def outer():
        return middle()

    def middle():
        return inner()

    def inner():
        log('doing inner work')
        return 42

Perhaps we want the logging to occur if we use the ``middle()`` funtion, but we
want the logging to be silent in ``outer()``.

One solution is to pass an argument through the call stack::

    def outer():
        return middle(verbose=False)

    def middle(verbose=True):
        return inner(verbose)

    def inner(verbose=True):
        if verbose:
            log('doing inner work')
        return 42

But now you'll need to include this argument in a ton of functions, or pass
through a ton of arguments.

Another solution is to have a global variable::

    _verbose = True

    def outer():
        _verbose = False
        return middle()

    def middle():
        return inner()

    def inner():
        if _verbose:
            log('doing inner work')
        return 42

But now you have a situation where some parts of the code can assign to the
global variable and never revert it, so it can be very difficult to tell where
``_verbose`` should be set or not.  Further, this is not threadsafe.

The approach this library takes is to have a global variable, but one which can
only be written to with a context manager entry, and which reverts its value
when the context is exited.  The variable is also handled delicately so its use
is threadsafe.  The implementation of this example would be::

    from dynamicscoping import dynamically_bound

    _verbose = dynamically_bound(True)

    def outer():
        with _verbose.binding(False):
            return middle()

    def middle():
        return inner()

    def inner():
        if _verbose.value:
            log('doing inner work')
        return 42


Usage
-----

Define a dynamically-bound variable::

    from dynamicscoping import dynamically_bound
    # ...
    var = dynamically_bound()

Define a dynamically-bound variable with an initial value::

    var = dynamically_bound('initial value')

Set its value in a given scope::

    with var.binding(42):
        do_stuff_with_var()

Retrieve the value (note that you can't simply do ``var``)::

    def do_stuff_with_var():
        return var.value


Examples
--------

These aren't "production-ready" examples, but they are meant to show some
possible uses for this library.

Pass recovery behavior on a given exception::

    from dynamicscoping import dynamically_bound

    # --- Setup ---

    recovery_behavior = dynamically_bound(lambda exception: raise exception)

    # --- Use ---

    def function_with_tunable_failures():
        try:
            do_stuff()
        except Exception as exception:
            recover = recovery_behavior.value
            return recover(exception)

    # --- Entry ---

    with recovery_behavior.binding(lambda _: '(no result)'):
        function_with_tunable_failures()

Decorator which allows toggleable caching::

    from dynamicscoping import dynamically_bound

    # --- Setup ---

    use_cache = dynamically_bound(False)
    cache = {}

    def _maybe_from_cache(func):
        @wraps(func)
        def _(box):
            if use_cache.value is not True:
                cache[func] = cache.get(func, {})
                cache[func][box] = func(box)
            return cache[func][box]
        return _

    # --- Use ---

    @_maybe_from_cache
    def inspect1(box):
        return expensive_op_1(box)

    @_maybe_from_cache
    def inspect2(box):
        return expensive_op_2(box)

    # --- Entry ---

    def do_inspection():
        with use_cache.binding(True):
            print(inspect1(box))
            print(inspect1(box))

You'll probably want to have some simple wrappers to clean up the interface a
little (you probably want to hide the use of ``binding`` per se)::

    from contextlib import contextmanager
    # ...

    @contextmanager
    def caching_enabled():
        with use_cache.binding(True):
            yield

    @contextmanager
    def caching_disabled():
        with use_cache.binding(False):
            yield

    def do_inspection():
        with caching_enabled():
            print(inspect1(box))
            with caching_disabled():
                print(inspect2(box))


Maintainer
----------

Med Mahmoud <medthehatta@gmail.com>

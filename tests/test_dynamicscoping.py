#!/usr/bin/env python
# coding: utf-8

"""Test dynamic scoping."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from dynamicscoping import UninitializedBinding
from dynamicscoping import dynamically_bound


#
# Helpers
#


def threaded_map(func, args):
    """Run a function `func` across `args` in parallel."""
    return list(ThreadPoolExecutor(max_workers=2).map(func, args))


#
# Fixtures
#


global_var_1 = dynamically_bound()


def some_function():
    """Return a dummy function returning the global variable."""
    return global_var_1.value


def some_function_ignoring_arg(x):
    """Return a dummy function returning the global variable."""
    return global_var_1.value


def some_function_nested(x):
    """Return a dummy function that will set the var to different things."""
    with global_var_1.binding(x):
        foo = global_var_1.value
        return foo


#
# Tests
#


def test_check_basic_use_case():
    """Check the basic use case."""
    var = dynamically_bound()
    with var.binding(3):
        assert var.value == 3


def test_check_binding_nested_once():
    """Check binding nested once."""
    var = dynamically_bound()
    with var.binding(3):
        with var.binding(5):
            assert var.value == 5
        assert var.value == 3


def test_check_binding_nested_twice():
    """Check binding nested twice."""
    var = dynamically_bound()
    with var.binding(3):
        with var.binding(5):
            with var.binding(7):
                assert var.value == 7
            assert var.value == 5
        assert var.value == 3


def test_behavior_in_function():
    """Check binding read from global scope by function."""
    with global_var_1.binding(3):
        assert some_function() == 3


def test_behavior_in_function_nested_once():
    """Check binding read from global scope by function (with nesting)."""
    with global_var_1.binding(3):
        with global_var_1.binding(5):
            assert some_function() == 5
        assert some_function() == 3


def test_behavior_in_function_nested_twice():
    """Check binding from global scope by function (with double nesting)."""
    with global_var_1.binding(3):
        with global_var_1.binding(5):
            with global_var_1.binding(7):
                assert some_function() == 7
            assert some_function() == 5
        assert some_function() == 3


def test_uninitialized():
    """Check that we can't derefrence an unbound var."""
    var = dynamically_bound()
    with pytest.raises(UninitializedBinding):
        var.value


def test_deinitialized():
    """Check we can't derefrence an unbound var even after prior binding."""
    var = dynamically_bound()
    with var.binding(5):
        assert var.value == 5
    with pytest.raises(UninitializedBinding):
        var.value


def test_threaded():
    """Test that the threads can set their variables independently."""
    values = list(range(1000))
    found = threaded_map(some_function_nested, values)
    assert found == values


def test_threaded_inherit_root():
    """Test that the threads can get the value from the root thread."""
    trials = 500
    with global_var_1.binding(12):
        found = threaded_map(some_function_ignoring_arg, list(range(trials)))
        assert found == [12] * trials


def test_threaded_inherit_root_nested():
    """Test threads can get the value from the root thread when nested."""
    trials = 500
    with global_var_1.binding(12):
        with global_var_1.binding(25):
            found = threaded_map(some_function_ignoring_arg,
                                 list(range(trials)))
            assert found == [25] * trials
        found2 = threaded_map(some_function_ignoring_arg, list(range(trials)))
        assert found2 == [12] * trials


def test_threaded_inherit_root_doubly_nested():
    """Test threads can get value from the root thread when doubly nested."""
    trials = 500
    with global_var_1.binding(666):
        with global_var_1.binding(12):
            with global_var_1.binding(25):
                found = threaded_map(some_function_ignoring_arg,
                                     list(range(trials)))
                assert found == [25] * trials
            found2 = threaded_map(some_function_ignoring_arg,
                                  list(range(trials)))
            assert found2 == [12] * trials
        found3 = threaded_map(some_function_ignoring_arg, list(range(trials)))
        assert found3 == [666] * trials


def test_named_var():
    """Test that we can store a name."""
    var = dynamically_bound(name='var')
    assert var._name in '{}'.format(var)


def test_value_in_repr():
    """Test that the value appears in the repr."""
    var = dynamically_bound()
    with var.binding(42):
        assert '42' in '{}'.format(var)


def test_binding_without_copy():
    """Test that we do not copy the value."""
    var = dynamically_bound()
    some_list = [1, 2, 3]
    with var.binding(some_list):
        assert var.value is some_list
        var.value.append(4)
        assert var.value == some_list
    # Original list has been mutated
    assert some_list == [1, 2, 3, 4]


def test_is_bound():
    """Test is_bound on a bound var."""
    var = dynamically_bound()
    # Before the context, it's unbound
    assert var.is_bound() is False

    # Inside the context, it's bound
    with var.binding('hi'):
        assert var.is_bound() is True

    # Outside the context again, it's unbound
    assert var.is_bound() is False

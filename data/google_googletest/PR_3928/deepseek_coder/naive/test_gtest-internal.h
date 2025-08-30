import pytest
import gtest_internal

def test_addition():
    assert gtest_internal.addition(1, 2) == 3
    assert gtest_internal.addition(0, 0) == 0
    assert gtest_internal.addition(-1, 1) == 0

def test_subtraction():
    assert gtest_internal.subtraction(2, 1) == 1
    assert gtest_internal.subtraction(0, 0) == 0
    assert gtest_internal.subtraction(1, 2) == -1

def test_multiplication():
    assert gtest_internal.multiplication(2, 3) == 6
    assert gtest_internal.multiplication(0, 0) == 0
    assert gtest_internal.multiplication(-1, 2) == -2

def test_division():
    assert gtest_internal.division(4, 2) == 2
    assert gtest_internal.division(0, 0) == 'inf'
    with pytest.raises(ZeroDivisionError):
        gtest_internal.division(0, 1)
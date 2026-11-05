
import pytest
from hypothesis import given, example, strategies as st

from elevator_dispatch import (
    parse_request,
    total_travel,
    load_percent
)


# Test 1: parse_request
@given(st.one_of(st.text(), st.none()))
@example(None)
@example("")
@example("5->9->10")
def test_parse_request_no_crash(s):
    try:
        parse_request(s)
    except ValueError:
        pass


# Test 2: total_travel
@given(st.one_of(st.text(), st.none()))
@example(None)
@example("")
@example("1,,3")
def test_total_travel_no_crash(s):
    try:
        total_travel(s)
    except ValueError:
        pass


# Test 3: load_percent
@given(st.one_of(st.text(), st.none()))
@example(None)
@example("")
@example("100 of 0")
def test_load_percent_no_crash(s):
    try:
        load_percent(s)
    except ValueError:
        pass


# Explicitly verify zero-capacity handling
def test_zero_capacity():
    with pytest.raises(ValueError):
        load_percent("100 of 0")

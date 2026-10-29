import pytest
from elevator_dispatch import next_direction, door_action, pick_elevator


# ============================================================================
# Tests for next_direction() - Line & Code Coverage
# ============================================================================

def test_next_direction_up_with_requests_above():
    """When moving up and there are requests above, continue up."""
    assert next_direction(3, "up", [5, 7]) == "up"


def test_next_direction_up_with_requests_below_only():
    """When moving up and there are only requests below, reverse to down."""
    assert next_direction(5, "up", [2, 1]) == "down"


def test_next_direction_up_with_no_requests():
    """When moving up and there are no requests, switch to idle."""
    assert next_direction(4, "up", []) == "idle"


def test_next_direction_up_with_request_at_current_floor_only():
    """When moving up with a request only at current floor, switch to idle."""
    assert next_direction(4, "up", [4]) == "idle"


def test_next_direction_down_with_requests_below():
    """When moving down and there are requests below, continue down."""
    assert next_direction(6, "down", [2, 4]) == "down"


def test_next_direction_down_with_requests_above_only():
    """When moving down and there are only requests above, reverse to up."""
    assert next_direction(2, "down", [5, 8]) == "up"


def test_next_direction_down_with_no_requests():
    """When moving down and there are no requests, switch to idle."""
    assert next_direction(3, "down", []) == "idle"


def test_next_direction_down_with_request_at_current_floor_only():
    """When moving down with a request only at current floor, switch to idle."""
    assert next_direction(3, "down", [3]) == "idle"


def test_next_direction_idle_with_requests_above():
    """When idle and there are requests above, set direction to up."""
    assert next_direction(2, "idle", [6, 1]) == "up"


def test_next_direction_idle_with_requests_below_only():
    """When idle and there are only requests below, set direction to down."""
    assert next_direction(7, "idle", [3, 1]) == "down"


def test_next_direction_idle_with_no_requests():
    """When idle and there are no requests, stay idle."""
    assert next_direction(5, "idle", []) == "idle"


def test_next_direction_idle_with_request_at_current_floor_only():
    """When idle and the only request is at current floor, stay idle."""
    assert next_direction(5, "idle", [5]) == "idle"


# ============================================================================
# Tests for door_action() - Line & Code Coverage
# ============================================================================

def test_door_action_emergency_priority():
    """Emergency takes priority over overload and blocked conditions."""
    assert door_action(700, True, True) == "hold_open"


def test_door_action_emergency_normal_load():
    """Emergency with normal load and not blocked holds door open."""
    assert door_action(200, False, True) == "hold_open"


def test_door_action_overload_strictly_above_630kg():
    """Load strictly above 630 kg triggers overload."""
    assert door_action(631, False, False) == "overload"
    assert door_action(750, True, False) == "overload"


def test_door_action_boundary_exact_630kg():
    """Exact 630 kg boundary is not overload; normal close if not blocked."""
    assert door_action(630, False, False) == "close"


def test_door_action_boundary_exact_630kg_blocked():
    """Exact 630 kg boundary reopens if blocked."""
    assert door_action(630, True, False) == "reopen"


def test_door_action_blocked_reopens():
    """Under 630 kg and blocked door triggers reopen."""
    assert door_action(400, True, False) == "reopen"


def test_door_action_normal_close():
    """Under 630 kg, not blocked, not emergency closes door."""
    assert door_action(350, False, False) == "close"


# ============================================================================
# Tests for pick_elevator() - Line & Code Coverage
# ============================================================================

def test_pick_elevator_empty_list():
    """Empty list of cars returns None."""
    assert pick_elevator([], 3) is None


def test_pick_elevator_single_car_idle():
    """Single idle car returns that car's name."""
    assert pick_elevator([("CarA", 2, True)], 5) == "CarA"


def test_pick_elevator_single_car_moving():
    """Single moving car returns that car's name."""
    assert pick_elevator([("CarB", 2, False)], 5) == "CarB"


def test_pick_elevator_closest_idle_car():
    """Picks closer idle car between multiple cars."""
    cars = [("CarA", 1, True), ("CarB", 6, True)]
    assert pick_elevator(cars, 5) == "CarB"


def test_pick_elevator_idle_penalty_causes_other_to_win():
    """Moving car incurs +5 penalty making idle car closer overall."""
    # CarA: pos 5, moving -> gap = |5 - 4| + 5 = 6
    # CarB: pos 1, idle   -> gap = |1 - 4| = 3
    cars = [("CarA", 5, False), ("CarB", 1, True)]
    assert pick_elevator(cars, 4) == "CarB"


def test_pick_elevator_moving_car_still_wins_if_much_closer():
    """Moving car wins if physical distance is much closer despite +5 penalty."""
    # CarA: pos 4, moving -> gap = |4 - 4| + 5 = 5
    # CarB: pos 15, idle  -> gap = |15 - 4| = 11
    cars = [("CarA", 4, False), ("CarB", 15, True)]
    assert pick_elevator(cars, 4) == "CarA"


def test_pick_elevator_tie_preserves_first_car():
    """When two cars have identical effective gaps, the first car is picked."""
    # CarA: pos 3, idle -> gap = |3 - 5| = 2
    # CarB: pos 7, idle -> gap = |7 - 5| = 2
    cars = [("CarA", 3, True), ("CarB", 7, True)]
    assert pick_elevator(cars, 5) == "CarA"


def test_pick_elevator_subsequent_car_has_larger_gap():
    """Second car has larger gap, so first car remains best."""
    # CarA: pos 5, idle -> gap = 0
    # CarB: pos 10, idle -> gap = 5
    cars = [("CarA", 5, True), ("CarB", 10, True)]
    assert pick_elevator(cars, 5) == "CarA"

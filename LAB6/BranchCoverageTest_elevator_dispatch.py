import pytest
from elevator_dispatch import next_direction, door_action, pick_elevator


# ============================================================================
# Branch Coverage Tests for next_direction()
# ============================================================================

def test_branch_direction_up_above_branch_taken():
    """Branch direction == 'up' -> True, above -> True."""
    # requests contains floors above and below to ensure list comprehension
    # evaluates both True and False for f > current and f < current
    assert next_direction(current=5, direction="up", requests=[3, 7]) == "up"


def test_branch_direction_up_above_false_below_true():
    """Branch direction == 'up' -> True, above -> False, below -> True."""
    assert next_direction(current=5, direction="up", requests=[2, 4]) == "down"


def test_branch_direction_up_both_empty_returns_idle():
    """Branch direction == 'up' -> True, above -> False, below -> False."""
    # Test with empty requests and request at current floor
    assert next_direction(current=5, direction="up", requests=[]) == "idle"
    assert next_direction(current=5, direction="up", requests=[5]) == "idle"


def test_branch_direction_down_below_branch_taken():
    """Branch direction == 'down' -> True, below -> True."""
    assert next_direction(current=5, direction="down", requests=[3, 8]) == "down"


def test_branch_direction_down_below_false_above_true():
    """Branch direction == 'down' -> True, below -> False, above -> True."""
    assert next_direction(current=5, direction="down", requests=[7, 9]) == "up"


def test_branch_direction_down_both_empty_returns_idle():
    """Branch direction == 'down' -> True, below -> False, above -> False."""
    assert next_direction(current=5, direction="down", requests=[]) == "idle"
    assert next_direction(current=5, direction="down", requests=[5]) == "idle"


def test_branch_direction_other_above_branch_taken():
    """Branch direction != 'up' and != 'down' (idle), above -> True."""
    assert next_direction(current=5, direction="idle", requests=[2, 8]) == "up"


def test_branch_direction_other_above_false_below_true():
    """Branch direction != 'up' and != 'down' (idle), above -> False, below -> True."""
    assert next_direction(current=5, direction="idle", requests=[1, 4]) == "down"


def test_branch_direction_other_both_empty_returns_idle():
    """Branch direction != 'up' and != 'down' (idle), above -> False, below -> False."""
    assert next_direction(current=5, direction="idle", requests=[]) == "idle"
    assert next_direction(current=5, direction="idle", requests=[5]) == "idle"


# ============================================================================
# Branch Coverage Tests for door_action()
# ============================================================================

def test_branch_door_action_emergency_true():
    """Branch emergency -> True (takes priority regardless of other inputs)."""
    assert door_action(load_kg=800, blocked=True, emergency=True) == "hold_open"
    assert door_action(load_kg=200, blocked=False, emergency=True) == "hold_open"


def test_branch_door_action_emergency_false_overload_true():
    """Branch emergency -> False, load_kg > 630 -> True."""
    assert door_action(load_kg=631, blocked=False, emergency=False) == "overload"
    assert door_action(load_kg=700, blocked=True, emergency=False) == "overload"


def test_branch_door_action_emergency_false_overload_false_blocked_true():
    """Branch emergency -> False, load_kg > 630 -> False, blocked -> True."""
    # Exactly on 630 kg boundary (not overloaded)
    assert door_action(load_kg=630, blocked=True, emergency=False) == "reopen"
    # Below 630 kg
    assert door_action(load_kg=500, blocked=True, emergency=False) == "reopen"


def test_branch_door_action_emergency_false_overload_false_blocked_false():
    """Branch emergency -> False, load_kg > 630 -> False, blocked -> False -> close."""
    # Exactly on 630 kg boundary
    assert door_action(load_kg=630, blocked=False, emergency=False) == "close"
    # Below 630 kg
    assert door_action(load_kg=150, blocked=False, emergency=False) == "close"


# ============================================================================
# Branch Coverage Tests for pick_elevator()
# ============================================================================

def test_branch_pick_elevator_empty_cars_loop_bypassed():
    """Branch for cars in pick_elevator: cars is empty (loop body 0 times)."""
    assert pick_elevator(cars=[], floor=3) is None


def test_branch_pick_elevator_single_car_idle_and_moving():
    """Loop 1 iteration: tests 'best is None' -> True with is_idle True and False."""
    # 1 iteration with is_idle == True (not is_idle is False)
    assert pick_elevator(cars=[("Car1", 4, True)], floor=4) == "Car1"

    # 1 iteration with is_idle == False (not is_idle is True, gap += 5)
    assert pick_elevator(cars=[("Car2", 4, False)], floor=4) == "Car2"


def test_branch_pick_elevator_gap_less_than_best_gap_true():
    """Subsequent iteration where gap < best_gap is True (updates best)."""
    cars = [
        ("CarA", 10, True),  # gap = 5
        ("CarB", 6, True),   # gap = 1 < 5 -> condition True, updates best
    ]
    assert pick_elevator(cars, floor=5) == "CarB"


def test_branch_pick_elevator_gap_less_than_best_gap_false():
    """Subsequent iteration where gap < best_gap is False (does not update best)."""
    cars = [
        ("CarA", 5, True),   # gap = 0 (best)
        ("CarB", 8, True),   # gap = 3 > 0 -> condition False, no update
        ("CarC", 2, True),   # gap = 3 > 0 -> condition False, no update
    ]
    assert pick_elevator(cars, floor=5) == "CarA"


def test_branch_pick_elevator_tie_gap_equals_best_gap():
    """Subsequent iteration where gap == best_gap (strict inequality is False)."""
    cars = [
        ("CarA", 3, True),   # gap = |3 - 5| = 2
        ("CarB", 7, True),   # gap = |7 - 5| = 2 (equal, not < best_gap)
    ]
    assert pick_elevator(cars, floor=5) == "CarA"


def test_branch_pick_elevator_moving_penalty_branch_interplay():
    """Both not is_idle True and False across multiple iterations."""
    cars = [
        ("CarA", 5, False),  # gap = |5 - 4| + 5 = 6 (best is None -> True)
        ("CarB", 1, True),   # gap = |1 - 4| = 3 < 6 -> True, updates best to CarB
        ("CarC", 9, False),  # gap = |9 - 4| + 5 = 10 > 3 -> False, no update
    ]
    assert pick_elevator(cars, floor=4) == "CarB"

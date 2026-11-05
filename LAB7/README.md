# Lab 7: Fuzzing for Input Validation Bugs

**Student Name:** Akash M P  
**SRN:** PES1UG24CS040  
**Course:** Software Engineering Lab  

---

## 1. Objective

The objective of this lab is to perform property-based fuzz testing on the elevator dispatch module (`elevator_dispatch.py`) using Python 3.12, `pytest`, and `Hypothesis`. The goal is to uncover unhandled edge-case bugs and crashes (such as `None` inputs, invalid types, malformed delimiters, and division by zero) and harden the application to handle invalid inputs gracefully by raising `ValueError` exceptions instead of crashing.

---

## 2. Functions Tested

The `elevator_dispatch.py` module contains three core functions:

1. **`parse_request(text)`**:
   - Parses a floor request string formatted as `FROM->TO` (e.g., `'5->9'`).
   - Returns a tuple of starting and destination floor numbers: `(start, end)`.

2. **`total_travel(floors_csv)`**:
   - Takes a comma-separated string of visited floor numbers (e.g., `'1,5,3,9'`).
   - Computes the total cumulative distance travelled between consecutive floors: `|5-1| + |3-5| + |9-3| = 12`.

3. **`load_percent(text)`**:
   - Parses elevator load and capacity given as `'LOAD of CAPACITY'` (e.g., `'450 of 630'`).
   - Computes the integer load percentage using integer division: `load * 100 // capacity`.

---

## 3. Bugs Found by Hypothesis Fuzz Testing

Running property-based tests in `test_elevator_dispatch.py` revealed four initial test failures across three main bug categories:

1. **`AttributeError` due to `None` inputs**:
   - The original functions assumed inputs were always strings and directly called `.split()`.
   - Passing `None` caused an unhandled `AttributeError: 'NoneType' object has no attribute 'split'` across all three functions (`test_parse_request_no_crash`, `test_total_travel_no_crash`, and `test_load_percent_no_crash`).

2. **`ZeroDivisionError` due to zero capacity**:
   - In `load_percent()`, the denominator was used in integer division `// int(capacity)` without checking if it was zero.
   - Input `'100 of 0'` raised an unhandled `ZeroDivisionError: integer division or modulo by zero` (`test_zero_capacity`).

3. **Missing Input Validation & Format Errors**:
   - Missing delimiters (e.g., empty string `""`) or extra delimiters (e.g., `'5->9->10'`) caused unpacking failures (`ValueError: not enough values to unpack` / `too many values to unpack`).
   - Empty tokens (e.g., `'1,,3'`) or non-numeric characters triggered unhandled `ValueError` inside integer comprehensions.
   - Negative floor numbers and cases where load exceeded capacity were accepted without validation.

---

## 4. Fixes Applied

The module was refactored with comprehensive defensive input validation:

- **`parse_request(text)`**:
  - Enforced string type validation (`isinstance(text, str)`); raises `ValueError("Input must be a string")` for `None` or non-string inputs.
  - Verified that splitting on `'->'` produces exactly two elements (`len(parts) == 2`).
  - Safely parsed floor values as integers inside `try...except ValueError`.
  - Added boundary validation ensuring floor numbers are non-negative (`start < 0 or end < 0`).

- **`total_travel(floors_csv)`**:
  - Enforced string type and non-empty validation (`not isinstance(floors_csv, str) or not floors_csv.strip()`).
  - Stripped whitespace and safely converted floor tokens inside `try...except ValueError`.
  - Enforced non-negative floor values (`any(f < 0 for f in floors)`).

- **`load_percent(text)`**:
  - Enforced string type validation and verified exact split into two parts on `' of '`.
  - Safely parsed load and capacity as integers.
  - Added boundary checks: `load < 0`, `capacity <= 0` (preventing `ZeroDivisionError`), and `load > capacity`.

---

## 5. Final Results

After implementing the input validations, all four Hypothesis test cases passed cleanly.

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ...\LAB7
plugins: anyio-4.13.0, hypothesis-6.170.14, asyncio-1.4.0
collected 4 items

test_elevator_dispatch.py::test_parse_request_no_crash PASSED            [ 25%]
test_elevator_dispatch.py::test_total_travel_no_crash PASSED             [ 50%]
test_elevator_dispatch.py::test_load_percent_no_crash PASSED             [ 75%]
test_elevator_dispatch.py::test_zero_capacity PASSED                     [100%]

============================== 4 passed in 0.94s ==============================
```

| Test Case | Before Fixes | After Fixes |
|-----------|--------------|-------------|
| `test_parse_request_no_crash` | **FAILED** (`AttributeError` on `None`, unpacking errors) | **PASSED** (Gracefully caught with `ValueError`) |
| `test_total_travel_no_crash` | **FAILED** (`AttributeError` on `None`, empty tokens) | **PASSED** (Gracefully caught with `ValueError`) |
| `test_load_percent_no_crash` | **FAILED** (`AttributeError` on `None`, `ZeroDivisionError`) | **PASSED** (Gracefully caught with `ValueError`) |
| `test_zero_capacity` | **FAILED** (`ZeroDivisionError` on `'100 of 0'`) | **PASSED** (Raises `ValueError` as expected) |
| **Total** | **4 FAILED** | **4 PASSED** |

---

## 6. Screenshots

- `Screenshots/01_original_application.png`: Original application output running with valid inputs.
- `Screenshots/02_fuzz_test_failures.png`: Initial pytest run showing 4 test failures caught by Hypothesis.
- `Screenshots/03_fixed_application.png`: Corrected application output running with valid inputs.
- `Screenshots/04_fixed_tests_passed.png`: Final pytest run showing all 4 tests passing in 0.94s.

---

## 7. Report Document

The complete formal practical report is available in PDF format:
- `Lab7_Fuzz_Testing_Report.pdf`

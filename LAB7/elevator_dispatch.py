
def parse_request(text):
    """Parse elevator request in FROM->TO format."""

    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    parts = text.split("->")

    if len(parts) != 2:
        raise ValueError("Invalid format. Use FROM->TO")

    try:
        start = int(parts[0].strip())
        end = int(parts[1].strip())
    except ValueError:
        raise ValueError("Floor numbers must be integers")

    if start < 0 or end < 0:
        raise ValueError("Floor numbers cannot be negative")

    return start, end


def total_travel(floors_csv):
    """Calculate total distance travelled between floors."""

    if not isinstance(floors_csv, str) or not floors_csv.strip():
        raise ValueError("Floor list cannot be empty")

    try:
        floors = [int(f.strip()) for f in floors_csv.split(",")]
    except ValueError:
        raise ValueError("All floor values must be integers")

    if any(f < 0 for f in floors):
        raise ValueError("Floor numbers cannot be negative")

    total = 0

    for i in range(len(floors) - 1):
        total += abs(floors[i + 1] - floors[i])

    return total


def load_percent(text):
    """Calculate elevator load percentage."""

    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    parts = text.split(" of ")

    if len(parts) != 2:
        raise ValueError("Use LOAD of CAPACITY format")

    try:
        load = int(parts[0].strip())
        capacity = int(parts[1].strip())
    except ValueError:
        raise ValueError("Load and capacity must be integers")

    if load < 0:
        raise ValueError("Load cannot be negative")

    if capacity <= 0:
        raise ValueError("Capacity must be greater than zero")

    if load > capacity:
        raise ValueError("Load cannot exceed capacity")

    return load * 100 // capacity


def main():
    print("==== Running parse_request ====")

    user_input = input(
        "Enter a request as FROM->TO (e.g. 5->9): "
    )

    try:
        result = parse_request(user_input)
        print("From and To:", result)
    except ValueError as e:
        print("Invalid request:", e)

    print("\n==== Running total_travel ====")

    user_input = input(
        "Enter floors visited as CSV (e.g. 1,5,3,9): "
    )

    try:
        result = total_travel(user_input)
        print("Floors Travelled:", result)
    except ValueError as e:
        print("Invalid floor list:", e)

    print("\n==== Running load_percent ====")

    user_input = input(
        "Enter load as 'X of Y' (e.g. 450 of 630): "
    )

    try:
        result = load_percent(user_input)
        print("Load Percent:", result)
    except ValueError as e:
        print("Invalid load:", e)


if __name__ == "__main__":
    main()

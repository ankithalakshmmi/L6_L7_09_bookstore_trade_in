import math

ASCII_DIGITS = "0123456789"

CONDITION_MULTIPLIERS = {
    "MINT": 1.25,
    "LIKE_NEW": 1.00,
    "VERY_GOOD": 0.80,
    "GOOD": 0.60,
    "POOR": 0.30,
}


def verify_isbn10_format(isbn_str):
    """Return a summary string for a well-formed ISBN-10, or None if the input is invalid."""
    if not isinstance(isbn_str, str):
        return None

    # Allow hyphens and spaces as separators only
    cleaned = isbn_str.replace('-', '').replace(' ', '').strip()

    # Must be exactly 10 characters
    if len(cleaned) != 10:
        return None

    # First 9 must be ASCII digits (str.isdigit() would accept '²', '٣' etc. which int() rejects)
    if not all(ch in ASCII_DIGITS for ch in cleaned[:9]):
        return None

    # Check character may be a digit or 'X' (meaning 10)
    check_char = cleaned[9].upper()
    if check_char not in ASCII_DIGITS and check_char != 'X':
        return None

    first_digit = int(cleaned[0])
    group_code = cleaned[1:4]
    return f"Group {group_code}: Starts {first_digit}, Checksum {check_char}"


def calculate_depreciation_factor(book_age_str):
    """Return a depreciation factor in [0.1, 1.0] for 'age/lifespan', or None if invalid."""
    if not isinstance(book_age_str, str):
        return None

    parts = book_age_str.split('/')
    if len(parts) != 2:
        return None

    try:
        age = float(parts[0])
        life = float(parts[1])
    except ValueError:
        return None

    # float() happily parses 'nan' and 'inf' -- reject them
    if not (math.isfinite(age) and math.isfinite(life)):
        return None

    # Lifespan must be positive (avoids ZeroDivisionError); age cannot be negative
    if life <= 0 or age < 0:
        return None

    depreciation = 1.0 - (age / life)
    return round(min(1.0, max(0.1, depreciation)), 2)


def lookup_condition_multiplier(condition_code):
    """Return the multiplier for a condition grade, or None if unknown/invalid."""
    if not isinstance(condition_code, str):
        return None

    # Normalise: trim, uppercase, treat spaces/hyphens as underscores ("like new" -> "LIKE_NEW")
    grade = condition_code.strip().upper().replace(' ', '_').replace('-', '_')
    return CONDITION_MULTIPLIERS.get(grade)


def main():
    print("==== Running verify_isbn10_format ====")
    isbn_in = input("Enter ISBN-10 (e.g. 0-306-40615-2): ")
    result = verify_isbn10_format(isbn_in)
    print(result if result is not None else "Invalid ISBN-10: need 9 digits followed by a digit or X.")

    print("\n==== Running calculate_depreciation_factor ====")
    age_in = input("Enter age/lifespan in years (e.g. 3/10): ")
    factor = calculate_depreciation_factor(age_in)
    if factor is not None:
        print("Depreciation Factor:", factor)
    else:
        print("Invalid input: use 'age/lifespan' with age >= 0 and lifespan > 0.")

    print("\n==== Running lookup_condition_multiplier ====")
    cond_in = input("Enter condition (e.g. MINT, GOOD, POOR): ")
    multiplier = lookup_condition_multiplier(cond_in)
    if multiplier is not None:
        print("Multiplier:", multiplier)
    else:
        print("Unknown condition. Valid options:", ", ".join(CONDITION_MULTIPLIERS))


if __name__ == "__main__":
    main()
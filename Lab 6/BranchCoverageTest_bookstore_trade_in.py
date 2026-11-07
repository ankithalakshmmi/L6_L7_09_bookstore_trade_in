"""Branch coverage tests for bookstore_trade_in.py
Goal: every decision (if / elif / for / break / continue) evaluates both True and False,
including boundary values and default (missing-key) paths.
"""
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def book(missing=0, condition="good", counterfeit=False):
    return {"missing_pages": missing, "condition": condition, "counterfeit": counterfeit}


def batch(fmt="paperback", books=None, approved=True, credit=False):
    return {"intake_approved": approved, "format": fmt,
            "payout_in_credit": credit, "books": books if books is not None else [book()]}


# ===================== process_book_buybacks =====================

# --- Branch 1: input validation (not list OR bonus < 0) ---
def test_branch_input_not_a_list():
    with pytest.raises(ValueError):
        process_book_buybacks({"a": 1}, 5.0)


def test_branch_negative_credit_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks([], -0.01)


def test_branch_zero_bonus_is_valid():
    # bonus == 0 boundary -> valid; empty list -> loop body never runs
    assert process_book_buybacks([], 0) == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


# --- Branch 2: intake_approved True / False / missing key ---
def test_branch_intake_not_approved():
    assert process_book_buybacks([batch(approved=False)], 0)["status"] == "ZERO_CREDIT"


def test_branch_intake_key_missing_defaults_false():
    assert process_book_buybacks([{"format": "paperback", "books": [book()]}], 0)["status"] == "ZERO_CREDIT"


# --- Branch 3: format if/elif/elif/else ---
@pytest.mark.parametrize("fmt, expected", [
    ("textbook", 40.0),
    ("hardcover", 15.0),
    ("paperback", 8.0),
])
def test_branch_each_format(fmt, expected):
    assert process_book_buybacks([batch(fmt=fmt)], 0) == {"total_payout": expected, "status": "COMPLETED"}


def test_branch_format_default_is_paperback():
    assert process_book_buybacks([{"intake_approved": True, "books": [book()]}], 0)["total_payout"] == 8.0


def test_branch_unknown_format_rejected():
    assert process_book_buybacks([batch(fmt="ebook")], 0)["status"] == "ZERO_CREDIT"


# --- Branch 4: books loop empty vs non-empty ---
def test_branch_empty_books_list():
    assert process_book_buybacks([batch(books=[])], 0)["status"] == "ZERO_CREDIT"


def test_branch_books_key_missing_but_credit_bonus_applies():
    b = {"intake_approved": True, "format": "hardcover", "payout_in_credit": True}
    assert process_book_buybacks([b], 3.0) == {"total_payout": 3.0, "status": "COMPLETED"}


# --- Branch 5: missing_pages > 0 (True / False, boundary 0 and 1) ---
def test_branch_missing_pages_boundary():
    res = process_book_buybacks([batch(books=[book(missing=0), book(missing=1)])], 0)
    assert res == {"total_payout": 8.0, "status": "COMPLETED"}


# --- Branch 6: counterfeit -> textbook break vs non-textbook continue ---
def test_branch_counterfeit_textbook_breaks_and_zeroes_batch():
    res = process_book_buybacks([batch(fmt="textbook", books=[book(condition="mint"), book(counterfeit=True), book()])], 0)
    assert res == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_branch_counterfeit_non_textbook_continues():
    res = process_book_buybacks([batch(fmt="hardcover", books=[book(counterfeit=True), book()])], 0)
    assert res == {"total_payout": 15.0, "status": "COMPLETED"}


# --- Branch 7: condition mint / poor / other ---
@pytest.mark.parametrize("cond, expected", [
    ("mint", 10.0),   # 8 * 1.25
    ("poor", 3.2),    # 8 * 0.40
    ("good", 8.0),
    ("fair", 8.0),    # unknown condition falls to else
])
def test_branch_conditions(cond, expected):
    assert process_book_buybacks([batch(books=[book(condition=cond)])], 0)["total_payout"] == expected


def test_branch_book_with_no_keys_uses_defaults():
    assert process_book_buybacks([batch(books=[{}])], 0)["total_payout"] == 8.0


# --- Branch 8: payout_in_credit True / False ---
def test_branch_payout_in_credit_true():
    assert process_book_buybacks([batch(credit=True)], 2.5)["total_payout"] == 10.5


def test_branch_payout_in_credit_false():
    assert process_book_buybacks([batch(credit=False)], 2.5)["total_payout"] == 8.0


# --- Branch 9: rejected_items > 4 (boundary 4 vs 5) ---
def test_branch_four_rejections_not_audited():
    books = [book(missing=1)] * 4 + [book()]
    assert process_book_buybacks([batch(books=books)], 0)["status"] == "COMPLETED"


def test_branch_five_rejections_audited():
    books = [book(missing=1)] * 3 + [book(counterfeit=True)] * 2 + [book()]
    assert process_book_buybacks([batch(books=books)], 0) == {"total_payout": 8.0, "status": "AUDIT_REJECTED"}


def test_branch_rejections_across_batches_with_unknown_format():
    batches = [batch(fmt="comic")] * 5
    assert process_book_buybacks(batches, 0) == {"total_payout": 0.0, "status": "AUDIT_REJECTED"}


# --- Branch 10: multiple batches mixed ---
def test_branch_multiple_batches_rounding():
    batches = [batch(fmt="paperback", books=[book(condition="poor")] * 3),  # 9.6
               batch(fmt="textbook", books=[book(condition="mint")], credit=True)]  # 50 + 1.111
    assert process_book_buybacks(batches, 1.111) == {"total_payout": 60.71, "status": "COMPLETED"}


# ===================== inspect_scanner_calibration =====================

def test_branch_scanner_empty_list():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_branch_scanner_none():
    assert inspect_scanner_calibration(None) == "NO_DATA"


def test_branch_scanner_device_with_no_readings():
    assert inspect_scanner_calibration([[]]) == "CALIBRATED"


def test_branch_scanner_boundary_5_is_ok():
    assert inspect_scanner_calibration([[5, 5, 5]]) == "CALIBRATED"


def test_branch_scanner_streak_reset():
    # single high reading, reset, single high reading -> never reaches streak 2
    assert inspect_scanner_calibration([[6, 1, 6, 1, 6]]) == "CALIBRATED"


def test_branch_scanner_two_consecutive_highs():
    assert inspect_scanner_calibration([[1, 6, 7, 1]]) == "RECALIBRATE"


def test_branch_streak_does_not_carry_across_devices():
    # last reading of device 1 high, first of device 2 high -> streak resets per device
    assert inspect_scanner_calibration([[1, 9], [9, 1]]) == "CALIBRATED"


def test_branch_second_device_triggers_recalibrate():
    assert inspect_scanner_calibration([[1, 2], [3, 8, 8]]) == "RECALIBRATE"

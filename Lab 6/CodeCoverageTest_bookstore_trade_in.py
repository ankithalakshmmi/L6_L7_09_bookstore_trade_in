"""Code (line) coverage tests for bookstore_trade_in.py
Goal: execute every statement at least once.
"""
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def book(missing=0, condition="good", counterfeit=False):
    return {"missing_pages": missing, "condition": condition, "counterfeit": counterfeit}


# ---------- process_book_buybacks ----------

def test_single_paperback_good():
    batches = [{"intake_approved": True, "format": "paperback",
                "payout_in_credit": False, "books": [book()]}]
    result = process_book_buybacks(batches, 5.0)
    assert result == {"total_payout": 8.0, "status": "COMPLETED"}


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        process_book_buybacks("not a list", 5.0)


def test_unapproved_batch_skipped_gives_zero_credit():
    batches = [{"intake_approved": False, "format": "paperback", "books": [book()]}]
    assert process_book_buybacks(batches, 5.0) == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_textbook_mint_with_credit_bonus():
    batches = [{"intake_approved": True, "format": "textbook",
                "payout_in_credit": True, "books": [book(condition="mint")]}]
    # 40 * 1.25 + 5 bonus = 55
    assert process_book_buybacks(batches, 5.0) == {"total_payout": 55.0, "status": "COMPLETED"}


def test_hardcover_poor():
    batches = [{"intake_approved": True, "format": "hardcover",
                "books": [book(condition="poor")]}]
    # 15 * 0.40 = 6
    assert process_book_buybacks(batches, 0) == {"total_payout": 6.0, "status": "COMPLETED"}


def test_unknown_format_rejected():
    batches = [{"intake_approved": True, "format": "magazine", "books": [book()]}]
    assert process_book_buybacks(batches, 0)["status"] == "ZERO_CREDIT"


def test_missing_pages_and_counterfeits_trigger_audit():
    batches = [{"intake_approved": True, "format": "paperback",
                "books": [book(missing=3), book(missing=1),
                          book(counterfeit=True), book(counterfeit=True),
                          book(counterfeit=True), book()]}]
    result = process_book_buybacks(batches, 0)
    assert result == {"total_payout": 8.0, "status": "AUDIT_REJECTED"}


def test_counterfeit_textbook_wipes_batch():
    batches = [{"intake_approved": True, "format": "textbook",
                "books": [book(), book(counterfeit=True), book()]}]
    assert process_book_buybacks(batches, 0) == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


# ---------- inspect_scanner_calibration ----------

def test_scanner_no_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_needs_recalibration():
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"


def test_scanner_calibrated():
    assert inspect_scanner_calibration([[1, 6, 2, 3]]) == "CALIBRATED"

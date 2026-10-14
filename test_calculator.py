import pytest
from datetime import date
from decimal import Decimal
from calculator import calculate_loan, calculate_default_limit

def test_loan_12_actual_days():
    res = calculate_loan(Decimal("5000"), "Bronze", date(2023, 1, 1), date(2023, 1, 13), Decimal("0"))
    assert res["actual_days"] == 12
    assert res["interest_days"] == 14
    assert res["interest"] == Decimal("630.00")
    assert res["payable_amount"] == Decimal("5630.00")

def test_loan_15_actual_days():
    res = calculate_loan(Decimal("5000"), "Bronze", date(2023, 1, 1), date(2023, 1, 16), Decimal("0"))
    assert res["actual_days"] == 15
    assert res["interest_days"] == 15
    assert res["interest"] == Decimal("675.00")
    assert res["payable_amount"] == Decimal("5675.00")

def test_loan_30_actual_days():
    res = calculate_loan(Decimal("5000"), "Bronze", date(2023, 1, 1), date(2023, 1, 31), Decimal("0"))
    assert res["actual_days"] == 30
    assert res["interest"] == Decimal("1350.00")
    assert res["payable_amount"] == Decimal("6350.00")

def test_loan_partial_payment_under():
    res = calculate_loan(Decimal("5000"), "Bronze", date(2023, 1, 1), date(2023, 1, 13), Decimal("1000"))
    assert res["payable_amount"] == Decimal("4630.00")
    assert res["excess_payment"] == Decimal("0.00")

def test_loan_partial_payment_over():
    res = calculate_loan(Decimal("5000"), "Bronze", date(2023, 1, 1), date(2023, 1, 13), Decimal("6000"))
    assert res["payable_amount"] == Decimal("0.00")
    assert res["excess_payment"] == Decimal("370.00")

def test_same_day_repayment():
    res = calculate_loan(Decimal("5000"), "Bronze", date(2023, 1, 1), date(2023, 1, 1), Decimal("0"))
    assert res["interest_days"] == 0
    assert res["interest"] == Decimal("0.00")

def test_default_limit_3_days():
    res = calculate_default_limit(Decimal("10000"), 3)
    assert res["total_days"] == 33
    assert res["retained_limit_pct"] == Decimal("100.00")
    assert res["final_limit"] == Decimal("10000")

def test_default_limit_4_days():
    res = calculate_default_limit(Decimal("10000"), 4)
    assert res["total_days"] == 34
    assert res["final_limit"] == Decimal("9400")

def test_default_limit_89_days():
    res = calculate_default_limit(Decimal("10000"), 89)
    assert res["total_days"] == 119
    assert res["final_limit"] == Decimal("6200")

def test_default_limit_90_days():
    res = calculate_default_limit(Decimal("10000"), 90)
    assert res["total_days"] == 120
    assert res["retained_limit_pct"] == Decimal("62.61")
    assert res["final_limit"] == Decimal("6200")

def test_default_limit_minimum_floor():
    res = calculate_default_limit(Decimal("5000"), 90)
    assert res["final_limit"] == Decimal("5000")
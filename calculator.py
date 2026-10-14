from decimal import Decimal, ROUND_HALF_UP
from datetime import date
import math

LOYALTY_RATES = {
    "Bronze": Decimal("0.009"),
    "Silver": Decimal("0.00875"),
    "Gold": Decimal("0.00825"),
    "Diamond": Decimal("0.0075")
}

def calculate_loan(principal: Decimal, loyalty_band: str, start_date: date, end_date: date, partial_payment: Decimal = Decimal('0')):
    if principal < Decimal('5000'):
        raise ValueError("Minimum loan amount is KSh 5,000.")
    if loyalty_band not in LOYALTY_RATES:
        raise ValueError("Unknown loyalty band.")
    if end_date < start_date:
        raise ValueError("End date cannot be earlier than start date.")
    if partial_payment < Decimal('0'):
        raise ValueError("Partial payment cannot be negative.")

    actual_days = (end_date - start_date).days
    
    if actual_days > 30:
        raise ValueError("Loan tenure exceeds maximum 30 days.")

    interest_days = 0 if actual_days == 0 else max(14, actual_days)
    daily_rate = LOYALTY_RATES[loyalty_band]
    
    raw_interest = principal * daily_rate * Decimal(interest_days)
    interest = raw_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    total_before_payment = principal + interest
    payable_amount = max(Decimal('0'), total_before_payment - partial_payment)
    excess_payment = max(Decimal('0'), partial_payment - total_before_payment)

    interest_30_raw = principal * daily_rate * Decimal(30)
    interest_30_days = interest_30_raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    expected_payment_30_days = principal + interest_30_days
    remaining_payment_30_days = max(Decimal('0'), expected_payment_30_days - partial_payment)

    return {
        "principal": principal,
        "daily_rate": daily_rate,
        "actual_days": actual_days,
        "interest_days": interest_days,
        "interest": interest,
        "total_before_payment": total_before_payment,
        "partial_payment": partial_payment,
        "payable_amount": payable_amount,
        "excess_payment": excess_payment,
        "interest_30_days": interest_30_days,
        "expected_payment_30_days": expected_payment_30_days,
        "remaining_payment_30_days": remaining_payment_30_days
    }

def calculate_default_limit(disbursement_amount: Decimal, days_in_default: int):
    if disbursement_amount < Decimal('5000'):
        raise ValueError("Disbursement amount must be at least KSh 5,000.")
    if days_in_default < 0:
        raise ValueError("Days in default cannot be negative.")

    A = disbursement_amount
    B = 30 + days_in_default
    C = Decimal('30') / Decimal(B) if B > 33 else Decimal('0')
    D = Decimal('1') - C
    E = D / Decimal('2') if B > 33 else Decimal('0')
    F = Decimal("0.6261") if B > 119 else Decimal('1') - E
    
    if B > 119:
        G = max(Decimal("5000"), Decimal("0.6260504202") * A)
    else:
        G = max(Decimal("5000"), F * A)
        
    H = Decimal(math.floor(G / Decimal('100'))) * Decimal('100')
    
    return {
        "original_amount": A,
        "days_in_default": days_in_default,
        "total_days": B,
        "retained_limit_pct": (F * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        "adjusted_amount": G.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        "final_limit": H
    }
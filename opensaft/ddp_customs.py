"""Norwegian MVA (25%) & EFTA Cross-Border DDP Landed Cost Calculator."""
from dataclasses import dataclass

@dataclass
class DDPQuote:
    fob_nok: float
    shipping_nok: float
    insurance_nok: float
    customs_value_nok: float
    duty_nok: float
    vat_base_nok: float
    mva_25_nok: float
    carrier_disbursement_nok: float
    total_ddp_nok: float

def calculate_norway_ddp(
    fob_amount: float,
    fx_rate_to_nok: float = 1.0,
    shipping_nok: float = 0.0,
    insurance_nok: float = 0.0,
    duty_rate: float = 0.0,
    vat_rate: float = 0.25,
    carrier_fee_nok: float = 195.0,
) -> DDPQuote:
    """
    Calculate exact Norwegian Tolletaten customs value (tollverdi) and 25% import MVA
    under Merverdiavgiftsloven § 4-11 and Tollavgiftsloven.
    """
    fob_nok = round(fob_amount * fx_rate_to_nok, 2)
    customs_val = round(fob_nok + shipping_nok + insurance_nok, 2)
    duty = round(customs_val * duty_rate, 2)
    vat_base = round(customs_val + duty, 2)
    mva = round(vat_base * vat_rate, 2)
    total = round(customs_val + duty + mva + carrier_fee_nok, 2)
    return DDPQuote(
        fob_nok=fob_nok,
        shipping_nok=round(shipping_nok, 2),
        insurance_nok=round(insurance_nok, 2),
        customs_value_nok=customs_val,
        duty_nok=duty,
        vat_base_nok=vat_base,
        mva_25_nok=mva,
        carrier_disbursement_nok=round(carrier_fee_nok, 2),
        total_ddp_nok=total,
    )

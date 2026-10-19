from opensaft.ddp_customs import calculate_norway_ddp
from opensaft.saft_generator import generate_saft_xml, validate_saft_balance

def test_ddp_calculation():
    q = calculate_norway_ddp(fob_amount=1000.0, fx_rate_to_nok=10.5, shipping_nok=500.0, insurance_nok=100.0)
    assert q.fob_nok == 10500.0
    assert q.customs_value_nok == 11100.0
    assert q.mva_25_nok == 2775.0
    assert q.total_ddp_nok == 14070.0

def test_saft_xml_generation_and_validation():
    rows = [
        {"date": "2026-10-01", "description": "Test Bilag", "debit_account": "6800", "credit_account": "1920", "debit": "1500.00", "credit": "1500.00"}
    ]
    xml_out = generate_saft_xml("999999999", "EXAMPLE ENK", rows, 2026)
    assert "<AuditFileVersion>1.30</AuditFileVersion>" in xml_out
    assert validate_saft_balance(xml_out) is True

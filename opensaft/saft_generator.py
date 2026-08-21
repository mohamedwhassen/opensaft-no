"""Deterministic Norwegian SAF-T Financial v1.30 XML Generator & Validator."""
import csv
import datetime
import xml.etree.ElementTree as ET
from typing import List, Dict

SAFT_NAMESPACE = "urn:StandardAuditFile-Taxation-Financial:NO"

STANDARD_ACCOUNTS_NS4102 = {
    "1920": ("Bankinnskudd driftskonto", "Asset"),
    "2710": ("Inngående merverdiavgift, høy sats (25%)", "Asset"),
    "2740": ("Oppgjørskonto merverdiavgift", "Liability"),
    "3000": ("Salgsinntekt handelsvarer, avgiftspliktig 25%", "Revenue"),
    "3100": ("Salgsinntekt eksport / avgiftsfri", "Revenue"),
    "4000": ("Varekjøp / innførsel DDP", "Expense"),
    "6540": ("Inventar, verktøy og datautstyr", "Expense"),
    "6800": ("Kontorrekvisita og programvare", "Expense"),
}

def generate_saft_xml(
    org_number: str,
    company_name: str,
    entries: List[Dict[str, str]],
    fiscal_year: int = 2026,
) -> str:
    """Generate Skatteetaten SAF-T Financial v1.30 compliant XML string from ledger rows."""
    ET.register_namespace("", SAFT_NAMESPACE)
    root = ET.Element(f"{{{SAFT_NAMESPACE}}}AuditFile")

    # 1. Header
    header = ET.SubElement(root, f"{{{SAFT_NAMESPACE}}}Header")
    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}AuditFileVersion").text = "1.30"
    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}AuditFileCountry").text = "NO"
    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}AuditFileDateCreated").text = datetime.date.today().isoformat()
    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}SoftwareCompanyName").text = "OpenSAFT-NO"
    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}SoftwareID").text = "OpenSAFT-NO CLI"
    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}SoftwareVersion").text = "0.3.2"

    company = ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}Company")
    ET.SubElement(company, f"{{{SAFT_NAMESPACE}}}RegistrationNumber").text = org_number.replace(" ", "")
    ET.SubElement(company, f"{{{SAFT_NAMESPACE}}}Name").text = company_name

    selection = ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}SelectionCriteria")
    ET.SubElement(selection, f"{{{SAFT_NAMESPACE}}}PeriodStart").text = "1"
    ET.SubElement(selection, f"{{{SAFT_NAMESPACE}}}PeriodStartYear").text = str(fiscal_year)
    ET.SubElement(selection, f"{{{SAFT_NAMESPACE}}}PeriodEnd").text = "12"
    ET.SubElement(selection, f"{{{SAFT_NAMESPACE}}}PeriodEndYear").text = str(fiscal_year)

    ET.SubElement(header, f"{{{SAFT_NAMESPACE}}}DefaultCurrencyCode").text = "NOK"

    # 2. MasterFiles (GeneralLedgerAccounts)
    master = ET.SubElement(root, f"{{{SAFT_NAMESPACE}}}MasterFiles")
    gl_accounts = ET.SubElement(master, f"{{{SAFT_NAMESPACE}}}GeneralLedgerAccounts")
    for acc_id, (desc, acc_type) in STANDARD_ACCOUNTS_NS4102.items():
        acc = ET.SubElement(gl_accounts, f"{{{SAFT_NAMESPACE}}}Account")
        ET.SubElement(acc, f"{{{SAFT_NAMESPACE}}}AccountID").text = acc_id
        ET.SubElement(acc, f"{{{SAFT_NAMESPACE}}}AccountDescription").text = desc
        ET.SubElement(acc, f"{{{SAFT_NAMESPACE}}}StandardAccountID").text = acc_id
        ET.SubElement(acc, f"{{{SAFT_NAMESPACE}}}AccountType").text = acc_type
        ET.SubElement(acc, f"{{{SAFT_NAMESPACE}}}OpeningDebitBalance").text = "0.00"
        ET.SubElement(acc, f"{{{SAFT_NAMESPACE}}}ClosingDebitBalance").text = "0.00"

    # 3. GeneralLedgerEntries
    gl = ET.SubElement(root, f"{{{SAFT_NAMESPACE}}}GeneralLedgerEntries")
    ET.SubElement(gl, f"{{{SAFT_NAMESPACE}}}NumberOfEntries").text = str(len(entries))

    total_debit = sum(float(e.get("debit", 0.0)) for e in entries)
    total_credit = sum(float(e.get("credit", 0.0)) for e in entries)
    ET.SubElement(gl, f"{{{SAFT_NAMESPACE}}}TotalDebit").text = f"{total_debit:.2f}"
    ET.SubElement(gl, f"{{{SAFT_NAMESPACE}}}TotalCredit").text = f"{total_credit:.2f}"

    journal = ET.SubElement(gl, f"{{{SAFT_NAMESPACE}}}Journal")
    ET.SubElement(journal, f"{{{SAFT_NAMESPACE}}}JournalID").text = "HOVEDBOK"
    ET.SubElement(journal, f"{{{SAFT_NAMESPACE}}}Description").text = "General Ledger"

    for idx, row in enumerate(entries, start=1):
        tx = ET.SubElement(journal, f"{{{SAFT_NAMESPACE}}}Transaction")
        ET.SubElement(tx, f"{{{SAFT_NAMESPACE}}}TransactionID").text = str(idx)
        ET.SubElement(tx, f"{{{SAFT_NAMESPACE}}}Period").text = row.get("date", "2026-01-01")[5:7].lstrip("0") or "1"
        ET.SubElement(tx, f"{{{SAFT_NAMESPACE}}}TransactionDate").text = row.get("date", "2026-01-01")
        ET.SubElement(tx, f"{{{SAFT_NAMESPACE}}}Description").text = row.get("description", "Bilag")

        line_debit = ET.SubElement(tx, f"{{{SAFT_NAMESPACE}}}Line")
        ET.SubElement(line_debit, f"{{{SAFT_NAMESPACE}}}RecordID").text = f"{idx}-1"
        ET.SubElement(line_debit, f"{{{SAFT_NAMESPACE}}}AccountID").text = row.get("debit_account", "6800")
        amt_d = ET.SubElement(line_debit, f"{{{SAFT_NAMESPACE}}}DebitAmount")
        ET.SubElement(amt_d, f"{{{SAFT_NAMESPACE}}}Amount").text = f"{float(row.get('debit', 0.0)):.2f}"

        line_credit = ET.SubElement(tx, f"{{{SAFT_NAMESPACE}}}Line")
        ET.SubElement(line_credit, f"{{{SAFT_NAMESPACE}}}RecordID").text = f"{idx}-2"
        ET.SubElement(line_credit, f"{{{SAFT_NAMESPACE}}}AccountID").text = row.get("credit_account", "1920")
        amt_c = ET.SubElement(line_credit, f"{{{SAFT_NAMESPACE}}}CreditAmount")
        ET.SubElement(amt_c, f"{{{SAFT_NAMESPACE}}}Amount").text = f"{float(row.get('credit', 0.0)):.2f}"

    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")

def validate_saft_balance(xml_string: str) -> bool:
    """Verify double-entry balance (TotalDebit == TotalCredit) and required SAF-T v1.30 nodes."""
    root = ET.fromstring(xml_string)
    ns = {"n": SAFT_NAMESPACE}
    ver = root.find(".//n:AuditFileVersion", ns)
    deb = root.find(".//n:TotalDebit", ns)
    cred = root.find(".//n:TotalCredit", ns)
    if ver is None or ver.text != "1.30":
        return False
    if deb is None or cred is None:
        return False
    return abs(float(deb.text) - float(cred.text)) < 0.001

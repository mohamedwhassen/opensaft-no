"""Command-line interface for OpenSAFT-NO."""
import argparse
import csv
import json
import sys
from opensaft.saft_generator import generate_saft_xml, validate_saft_balance
from opensaft.ddp_customs import calculate_norway_ddp

def main():
    parser = argparse.ArgumentParser(description="OpenSAFT-NO: Norwegian SAF-T v1.30 XML & DDP Customs CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ddp = sub.add_parser("ddp", help="Calculate Norwegian 25% MVA DDP landed cost")
    p_ddp.add_argument("--fob", type=float, required=True, help="FOB value in source currency")
    p_ddp.add_argument("--fx", type=float, default=1.0, help="Exchange rate to NOK")
    p_ddp.add_argument("--shipping", type=float, default=450.0, help="Shipping in NOK")
    p_ddp.add_argument("--insurance", type=float, default=150.0, help="Insurance in NOK")

    p_saft = sub.add_parser("export-saft", help="Convert CSV ledger to SAF-T v1.30 XML")
    p_saft.add_argument("--csv", required=True, help="Input CSV ledger path")
    p_saft.add_argument("--org", default="999999999", help="Norwegian 9-digit Org.nr.")
    p_saft.add_argument("--name", default="EXAMPLE ENK", help="Company / ENK name")
    p_saft.add_argument("--out", required=True, help="Output XML file path")

    args = parser.parse_args()
    if args.cmd == "ddp":
        q = calculate_norway_ddp(args.fob, args.fx, args.shipping, args.insurance)
        print(json.dumps(q.__dict__, indent=2))
    elif args.cmd == "export-saft":
        with open(args.csv, newline="", encoding="utf-8") as f:
            entries = list(csv.DictReader(f))
        xml_str = generate_saft_xml(args.org, args.name, entries)
        if not validate_saft_balance(xml_str):
            sys.exit("ERROR: Double-entry ledger out of balance (TotalDebit != TotalCredit)")
        with open(args.out, "w", encoding="utf-8") as out_f:
            out_f.write(xml_str)
        print(f"OK: Generated valid SAF-T v1.30 XML ({len(entries)} transactions) -> {args.out}")

if __name__ == "__main__":
    main()

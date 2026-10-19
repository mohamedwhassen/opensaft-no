# OpenSAFT-NO (`v0.3.2`)

**Open-Source SAF-T Financial v1.30 XML Generator, NS 4102 Ledger Validator & DDP/MVA Customs Engine**

## Overview
**OpenSAFT-NO** is a lightweight, zero-telemetry, open-source (MIT) Python library and CLI utility that:
1. Converts standard CSV ledgers into validated **SAF-T Financial v1.30 XML** mapped to **NS 4102** (*Norsk Standard Kontoplan*).
2. Verifies double-entry balance (`TotalDebit == TotalCredit`) and standard MVA tax codes locally.
3. Computes exact **DDP landed costs** (`Tollverdi + 25% Inngående MVA`) for cross-border imports.

## Quickstart

```bash
# 1. Calculate 25% MVA DDP landed cost
python3 -m opensaft.cli ddp --fob 1200 --fx 10.55 --shipping 450 --insurance 150

# 2. Convert a CSV ledger into a validated SAF-T v1.30 XML file
python3 -m opensaft.cli export-saft --csv examples/sample_ledger_2026.csv --org 999999999 --name "EXAMPLE ENK" --out audit_saft_2026.xml
```

## License
MIT License.

#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP

latest = {}  # txn_id -> latest event

with open("payments.jsonl", encoding="utf-8-sig") as f:
    for line in f:
        try:
            event = json.loads(line)
        except ValueError:
            continue  # unreadable line
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue  # no txn_id
        prev = latest.get(event["txn_id"])
        # ts is uniform ISO-8601 UTC, so string comparison orders correctly
        if prev is None or event["ts"] >= prev["ts"]:
            latest[event["txn_id"]] = event


def parse_amount(value):
    # amounts arrive as numbers or strings like "55,707.77"
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return Decimal(str(value))


total = Decimal(0)
count = 0
for event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{int(total.quantize(Decimal(1), rounding=ROUND_HALF_UP))}")

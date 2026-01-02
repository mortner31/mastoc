#!/usr/bin/env python3
"""
Resync holds tape data from local JSON file.

This script updates existing holds with the tape_str data from montoboard_setup.json.

Usage:
    python scripts/resync_holds_tape.py
"""

import os
import sys
import json

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mastoc_api.database import SessionLocal
from mastoc_api.models import Hold


# Path to local setup JSON
SETUP_JSON = os.path.join(
    os.path.dirname(__file__), "..", "..", "extracted", "data", "montoboard_setup.json"
)


def resync_holds_tape():
    """Update holds with tape data from local JSON."""
    print("=== Resync Holds Tape Data ===\n")

    # Load local JSON
    print(f"Loading {SETUP_JSON}...")
    with open(SETUP_JSON, "r") as f:
        setup = json.load(f)

    holds_data = setup.get("holds", [])
    print(f"Found {len(holds_data)} holds in JSON")

    db = SessionLocal()
    total_updated = 0

    try:
        for hold_data in holds_data:
            stokt_id = hold_data.get("id")
            center_tape = hold_data.get("centerTapeStr", "")
            right_tape = hold_data.get("rightTapeStr", "")
            left_tape = hold_data.get("leftTapeStr", "")

            # Find hold in database by stokt_id
            hold = db.query(Hold).filter(Hold.stokt_id == stokt_id).first()
            if not hold:
                continue

            # Update tape data
            hold.center_tape_str = center_tape if center_tape else None
            hold.right_tape_str = right_tape if right_tape else None
            hold.left_tape_str = left_tape if left_tape else None
            total_updated += 1

        db.commit()
        print(f"Updated {total_updated} holds")

    finally:
        db.close()

    print(f"\n=== Done! Updated {total_updated} holds ===")


if __name__ == "__main__":
    resync_holds_tape()

#!/usr/bin/env python3
"""
Resync holds tape data from Stokt.

This script updates existing holds with the tape_str data from Stokt API.

Usage:
    python scripts/resync_holds_tape.py
"""

import os
import sys

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "mastoc", "src"))

from sqlalchemy import text
from mastoc_api.database import engine, SessionLocal
from mastoc_api.models import Hold, Face
from mastoc.api.client import StoktAPI, MONTOBOARD_GYM_ID


def resync_holds_tape():
    """Update holds with tape data from Stokt."""
    print("=== Resync Holds Tape Data ===\n")

    # Connect to Stokt API
    api = StoktAPI()

    # Get face setup from Stokt
    print("Fetching gym walls from Stokt...")
    walls = api.get_gym_walls(MONTOBOARD_GYM_ID)
    print(f"Found {len(walls)} walls")

    db = SessionLocal()
    total_updated = 0

    try:
        for wall in walls:
            for stokt_face_id in wall.faces:
                print(f"\nProcessing face {stokt_face_id}...")

                # Get face setup with holds
                face_setup = api.get_face_setup(stokt_face_id)
                if not face_setup:
                    print(f"  Could not get face setup, skipping")
                    continue

                print(f"  Found {len(face_setup.holds)} holds")

                # Update each hold
                for stokt_hold in face_setup.holds:
                    # Find hold in database by stokt_id
                    hold = db.query(Hold).filter(Hold.stokt_id == stokt_hold.id).first()
                    if not hold:
                        continue

                    # Update tape data
                    hold.center_tape_str = stokt_hold.center_tape_str or None
                    hold.right_tape_str = stokt_hold.right_tape_str or None
                    hold.left_tape_str = stokt_hold.left_tape_str or None
                    total_updated += 1

                db.commit()
                print(f"  Updated {total_updated} holds so far")

    finally:
        db.close()

    print(f"\n=== Done! Updated {total_updated} holds ===")


if __name__ == "__main__":
    resync_holds_tape()

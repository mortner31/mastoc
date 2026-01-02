#!/usr/bin/env python3
"""
Migration: Add tape_str columns to holds table.

Run this script to add the center_tape_str, right_tape_str, left_tape_str
columns to the holds table.

Usage:
    python scripts/migrate_add_tape_str.py
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import text
from mastoc_api.database import engine


def migrate():
    """Add tape_str columns to holds table."""
    columns = [
        ("center_tape_str", "VARCHAR(200)"),
        ("right_tape_str", "VARCHAR(200)"),
        ("left_tape_str", "VARCHAR(200)"),
    ]

    with engine.connect() as conn:
        for col_name, col_type in columns:
            # Check if column exists
            result = conn.execute(text(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'holds' AND column_name = '{col_name}'
            """))

            if result.fetchone() is None:
                print(f"Adding column {col_name}...")
                conn.execute(text(f"""
                    ALTER TABLE holds ADD COLUMN {col_name} {col_type}
                """))
                conn.commit()
                print(f"  Column {col_name} added.")
            else:
                print(f"  Column {col_name} already exists, skipping.")

    print("Migration complete!")


if __name__ == "__main__":
    migrate()

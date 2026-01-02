#!/usr/bin/env python3
"""
Script de correction des dates created_at des climbs via SQL direct.

Utilise le backup Stokt local pour récupérer les vraies dates de création.

Usage:
    python scripts/fix_climb_dates_sql.py
    python scripts/fix_climb_dates_sql.py --dry-run
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

# Configuration
BACKUP_FILE = Path(__file__).parent.parent.parent / "data" / "stokt_backup" / "montoboard_ALL_climbs.json"


def load_stokt_dates() -> dict[str, str]:
    """Charge les dates depuis le backup Stokt."""
    if not BACKUP_FILE.exists():
        raise FileNotFoundError(f"Backup file not found: {BACKUP_FILE}")

    data = json.loads(BACKUP_FILE.read_text())

    # Créer un mapping stokt_id -> dateCreated
    dates = {}
    for climb in data["climbs"]:
        stokt_id = climb["id"]
        date_created = climb.get("dateCreated", "")
        if date_created:
            dates[stokt_id] = date_created

    print(f"Chargé {len(dates)} dates depuis {BACKUP_FILE.name}")
    return dates


def main():
    parser = argparse.ArgumentParser(description="Fix climb dates from Stokt backup (SQL direct)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update")
    args = parser.parse_args()

    # Charger .env
    load_dotenv(Path(__file__).parent.parent / ".env")
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not found in environment")

    # Charger les dates Stokt
    stokt_dates = load_stokt_dates()

    # Connexion à la base
    print("\n=== Connexion à la base ===")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # Récupérer les climbs avec date d'import
    print("\n=== Récupération des climbs ===")
    import_date = "2025-12-30"

    cursor.execute("""
        SELECT id, stokt_id, name, created_at
        FROM climbs
        WHERE created_at::text LIKE %s
        AND stokt_id IS NOT NULL
    """, (f"{import_date}%",))

    climbs = cursor.fetchall()
    print(f"{len(climbs)} climbs avec date d'import trouvés")

    # Préparer les corrections
    updates = []
    for climb_id, stokt_id, name, current_date in climbs:
        real_date = stokt_dates.get(str(stokt_id))
        if real_date:
            updates.append((climb_id, stokt_id, name, real_date))

    print(f"{len(updates)} climbs à corriger")

    if not updates:
        print("Aucune correction nécessaire!")
        cursor.close()
        conn.close()
        return

    # Afficher quelques exemples
    print("\nExemples de corrections:")
    for _, _, name, new_date in updates[:5]:
        print(f"  {name[:30]:30} -> {new_date[:10]}")

    if args.dry_run:
        print("\n[DRY RUN] Aucune modification effectuée")
        cursor.close()
        conn.close()
        return

    # Appliquer les corrections
    print("\n=== Application des corrections ===")
    updated = 0
    errors = 0

    for climb_id, stokt_id, name, new_date in updates:
        try:
            # Parser la date
            parsed_date = datetime.fromisoformat(new_date.replace("Z", "+00:00"))

            cursor.execute("""
                UPDATE climbs
                SET created_at = %s
                WHERE id = %s
            """, (parsed_date, climb_id))
            updated += 1

        except Exception as e:
            errors += 1
            print(f"  Erreur {name}: {e}")

        if updated % 100 == 0 and updated > 0:
            print(f"  Progress: {updated}/{len(updates)}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nRésultat: {updated} corrigés, {errors} erreurs")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Migration : Ajout champs auth au modèle User.

Ce script ajoute les colonnes nécessaires pour l'authentification JWT :
- email, username, password_hash
- is_active, role
- updated_at, last_login_at
- reset_token, reset_token_expires

Usage:
    python scripts/migrate_user_auth.py

    # Dry-run (voir les requêtes sans les exécuter)
    python scripts/migrate_user_auth.py --dry-run
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text
from mastoc_api.database import engine


MIGRATIONS = [
    # Users - colonnes
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user'",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP",
    # Users - index (après les colonnes)
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email) WHERE email IS NOT NULL",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username) WHERE username IS NOT NULL",
    # Climbs - traçabilité
    "ALTER TABLE climbs ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES users(id)",
    "ALTER TABLE climbs ADD COLUMN IF NOT EXISTS updated_by_id UUID REFERENCES users(id)",
    "ALTER TABLE climbs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
]


def run_migration(dry_run: bool = False):
    """Exécute la migration."""
    print("Migration: Ajout champs auth au modèle User")
    print("=" * 50)

    if dry_run:
        print("\n[DRY-RUN] Requêtes SQL qui seront exécutées:\n")
        for stmt in MIGRATIONS:
            print(f"  - {stmt}")
        return

    # Exécuter les migrations une par une avec commit individuel
    success = 0
    skipped = 0
    errors = 0

    for stmt in MIGRATIONS:
        with engine.connect() as conn:
            try:
                print(f"Executing: {stmt[:60]}...")
                conn.execute(text(stmt))
                conn.commit()
                print("  ✓ OK")
                success += 1
            except Exception as e:
                conn.rollback()
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"  → Already exists (skipped)")
                    skipped += 1
                else:
                    print(f"  ✗ Error: {e}")
                    errors += 1

    print("\n" + "=" * 50)
    print(f"Migration terminée! {success} OK, {skipped} skipped, {errors} errors")


def main():
    parser = argparse.ArgumentParser(description="Migration auth User")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher les requêtes sans les exécuter"
    )
    args = parser.parse_args()

    run_migration(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

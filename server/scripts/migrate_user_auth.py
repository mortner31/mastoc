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


MIGRATION_SQL = """
-- Migration: Add auth columns to users table
-- Date: 2025-12-31

-- =========================================
-- Users table
-- =========================================

-- Email (unique, indexed)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

-- Username (unique, indexed)
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100) UNIQUE;
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

-- Password hash
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Account status
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Role (user/admin)
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';

-- Timestamps
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

-- Reset password
ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP;

-- =========================================
-- Climbs table (traçabilité)
-- =========================================

-- Created by (utilisateur mastoc qui a créé)
ALTER TABLE climbs ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES users(id);

-- Updated by (dernier utilisateur à modifier)
ALTER TABLE climbs ADD COLUMN IF NOT EXISTS updated_by_id UUID REFERENCES users(id);

-- Updated at (date de dernière modification)
ALTER TABLE climbs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
"""


def run_migration(dry_run: bool = False):
    """Exécute la migration."""
    print("Migration: Ajout champs auth au modèle User")
    print("=" * 50)

    if dry_run:
        print("\n[DRY-RUN] Requêtes SQL qui seront exécutées:\n")
        print(MIGRATION_SQL)
        return

    # Exécuter les migrations
    with engine.connect() as conn:
        # Split par requête (chaque ligne qui ne commence pas par --)
        statements = [
            stmt.strip()
            for stmt in MIGRATION_SQL.split(';')
            if stmt.strip() and not stmt.strip().startswith('--')
        ]

        for stmt in statements:
            try:
                print(f"Executing: {stmt[:60]}...")
                conn.execute(text(stmt))
                print("  ✓ OK")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  → Already exists (skipped)")
                else:
                    print(f"  ✗ Error: {e}")

        conn.commit()

    print("\n" + "=" * 50)
    print("Migration terminée!")


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

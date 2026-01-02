#!/usr/bin/env python3
"""
Script de correction des dates created_at des climbs.

Utilise le backup Stokt local pour récupérer les vraies dates de création.

Usage:
    python scripts/fix_climb_dates.py --api-key YOUR_KEY
    python scripts/fix_climb_dates.py --api-key YOUR_KEY --dry-run
"""

import argparse
import json
from pathlib import Path

import httpx

# Configuration
MASTOC_API_URL = "https://mastoc-production.up.railway.app"
BACKUP_FILE = Path(__file__).parent.parent.parent / "data" / "stokt_backup" / "montoboard_ALL_climbs.json"
BATCH_SIZE = 100


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


def get_all_climbs(client: httpx.Client) -> list[dict]:
    """Récupère tous les climbs depuis l'API."""
    all_climbs = []
    page = 1
    page_size = 500

    while True:
        response = client.get(
            f"{MASTOC_API_URL}/api/climbs",
            params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        data = response.json()
        all_climbs.extend(data["results"])

        if len(data["results"]) < page_size:
            break
        page += 1

    return all_climbs


def bulk_update_dates(client: httpx.Client, updates: list[dict]) -> dict:
    """Met à jour les dates en masse."""
    response = client.patch(
        f"{MASTOC_API_URL}/api/climbs/bulk/dates",
        json={"updates": updates},
        timeout=120
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Fix climb dates from Stokt backup")
    parser.add_argument("--api-key", required=True, help="mastoc-api API Key")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update")
    args = parser.parse_args()

    # Charger les dates Stokt
    stokt_dates = load_stokt_dates()

    # Client API
    headers = {"X-API-Key": args.api_key}
    client = httpx.Client(timeout=60, headers=headers)

    # Vérifier l'API
    print("\n=== Vérification API ===")
    health = client.get(f"{MASTOC_API_URL}/health").json()
    print(f"Status: {health['status']}")

    # Récupérer les climbs actuels
    print("\n=== Récupération des climbs ===")
    climbs = get_all_climbs(client)
    print(f"{len(climbs)} climbs dans la base")

    # Analyser les dates à corriger
    print("\n=== Analyse des dates ===")
    updates = []
    import_date = "2025-12-30"  # Date d'import initiale

    for climb in climbs:
        stokt_id = climb.get("stokt_id")
        current_date = climb.get("created_at", "")

        if not stokt_id:
            continue

        # Vérifier si la date actuelle est celle de l'import
        if current_date and current_date.startswith(import_date):
            real_date = stokt_dates.get(stokt_id)
            if real_date:
                updates.append({
                    "stokt_id": stokt_id,
                    "created_at": real_date,
                    "name": climb["name"]  # Pour affichage
                })

    print(f"{len(updates)} climbs à corriger")

    if not updates:
        print("Aucune correction nécessaire!")
        return

    # Afficher quelques exemples
    print("\nExemples de corrections:")
    for item in updates[:5]:
        print(f"  {item['name'][:30]:30} -> {item['created_at'][:10]}")

    if args.dry_run:
        print("\n[DRY RUN] Aucune modification effectuée")
        return

    # Appliquer les corrections par batch
    print("\n=== Application des corrections ===")
    total_updated = 0
    total_errors = 0

    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i + BATCH_SIZE]
        # Retirer le champ 'name' qui n'est pas nécessaire pour l'API
        api_batch = [{"stokt_id": u["stokt_id"], "created_at": u["created_at"]} for u in batch]

        result = bulk_update_dates(client, api_batch)
        total_updated += result["updated"]
        total_errors += result["errors"]

        print(f"  Batch {i // BATCH_SIZE + 1}: {result['updated']} mis à jour, {result['errors']} erreurs")

    print(f"\nRésultat: {total_updated} corrigés, {total_errors} erreurs")


if __name__ == "__main__":
    main()

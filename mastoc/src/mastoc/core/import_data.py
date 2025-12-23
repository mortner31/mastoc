"""
Script d'import des données JSON vers SQLite.

Importe les fichiers extraits de l'API Stokt vers la base locale.
"""

import json
from pathlib import Path
from datetime import datetime

from mastoc.api.models import Climb, Face
from mastoc.db import Database, ClimbRepository, HoldRepository


def import_climbs_from_json(json_path: Path, db: Database, callback=None) -> int:
    """
    Importe les climbs depuis un fichier JSON.

    Args:
        json_path: Chemin du fichier JSON (montoboard_ALL_climbs.json)
        db: Instance de Database
        callback: Fonction appelée avec (current, total)

    Returns:
        Nombre de climbs importés
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    # Le fichier peut être soit une liste, soit un dict avec clé "climbs"
    if isinstance(data, dict):
        data = data.get("climbs", data.get("results", []))

    climbs = [Climb.from_api(c) for c in data]
    repo = ClimbRepository(db)
    repo.save_climbs(climbs, callback=callback)

    db.set_last_sync()
    return len(climbs)


def import_setup_from_json(json_path: Path, db: Database) -> int:
    """
    Importe le setup (face + prises) depuis un fichier JSON.

    Args:
        json_path: Chemin du fichier JSON (montoboard_setup.json)
        db: Instance de Database

    Returns:
        Nombre de prises importées
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    face = Face.from_api(data)
    repo = HoldRepository(db)
    repo.save_face(face)

    return len(face.holds)


def import_all_data(data_dir: Path, db_path: Path = None, verbose: bool = True) -> dict:
    """
    Importe toutes les données depuis le répertoire extracted/data.

    Args:
        data_dir: Répertoire contenant les fichiers JSON
        db_path: Chemin de la base SQLite (optionnel)
        verbose: Afficher la progression

    Returns:
        Dict avec statistiques d'import
    """
    db = Database(db_path) if db_path else Database()

    stats = {"climbs": 0, "holds": 0, "errors": []}

    # Import setup (prises)
    setup_file = data_dir / "montoboard_setup.json"
    if setup_file.exists():
        if verbose:
            print(f"Import setup depuis {setup_file}...")
        try:
            stats["holds"] = import_setup_from_json(setup_file, db)
            if verbose:
                print(f"  {stats['holds']} prises importées")
        except Exception as e:
            stats["errors"].append(f"setup: {e}")
            if verbose:
                print(f"  Erreur: {e}")

    # Import climbs
    climbs_file = data_dir / "montoboard_ALL_climbs.json"
    if climbs_file.exists():
        if verbose:
            print(f"Import climbs depuis {climbs_file}...")

        def progress(current, total):
            if verbose and current % 200 == 0:
                print(f"  {current}/{total} climbs...")

        try:
            stats["climbs"] = import_climbs_from_json(climbs_file, db, callback=progress)
            if verbose:
                print(f"  {stats['climbs']} climbs importés")
        except Exception as e:
            stats["errors"].append(f"climbs: {e}")
            if verbose:
                print(f"  Erreur: {e}")

    if verbose:
        print(f"\nImport terminé:")
        print(f"  - {stats['climbs']} climbs")
        print(f"  - {stats['holds']} prises")
        print(f"  - Base: {db.db_path}")

    return stats


if __name__ == "__main__":
    # Script exécutable directement
    import sys

    # Chercher le répertoire de données
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    data_dir = repo_root / "extracted" / "data"

    if not data_dir.exists():
        print(f"Répertoire de données non trouvé: {data_dir}")
        sys.exit(1)

    stats = import_all_data(data_dir)

    if stats["errors"]:
        print(f"\nErreurs: {stats['errors']}")
        sys.exit(1)

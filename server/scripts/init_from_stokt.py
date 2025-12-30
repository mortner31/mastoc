#!/usr/bin/env python3
"""
Script d'import initial des données Stokt vers mastoc-api.

Usage:
    python scripts/init_from_stokt.py --username USER --password PASS

Ou avec token existant:
    python scripts/init_from_stokt.py --token TOKEN

Avec API Key (si configurée sur Railway):
    python scripts/init_from_stokt.py --token TOKEN --api-key YOUR_API_KEY

Avec cache (évite de re-télécharger depuis Stokt):
    python scripts/init_from_stokt.py --token TOKEN --api-key KEY --use-cache
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du client mastoc
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mastoc" / "src"))

import httpx
from mastoc.api.client import StoktAPI, MONTOBOARD_GYM_ID


# Configuration
MASTOC_API_URL = "https://mastoc-production.up.railway.app"
API_KEY_HEADER = "X-API-Key"
CACHE_DIR = Path(__file__).parent / ".cache"


def get_cache_path(name: str) -> Path:
    """Retourne le chemin du fichier cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"{name}.json"


def save_to_cache(name: str, data: list):
    """Sauvegarde les données en cache."""
    cache_path = get_cache_path(name)

    # Convertir les objets en dicts sérialisables
    serializable = []
    for item in data:
        if hasattr(item, '__dict__'):
            d = {}
            for k, v in item.__dict__.items():
                if hasattr(v, '__dict__'):
                    d[k] = v.__dict__
                else:
                    d[k] = v
            serializable.append(d)
        else:
            serializable.append(item)

    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "count": len(data),
        "data": serializable
    }
    cache_path.write_text(json.dumps(cache_data, indent=2, default=str))
    print(f"  Cache sauvegardé: {cache_path} ({len(data)} items)")


def load_from_cache(name: str) -> list | None:
    """Charge les données depuis le cache."""
    cache_path = get_cache_path(name)
    if not cache_path.exists():
        return None

    cache_data = json.loads(cache_path.read_text())
    print(f"  Cache chargé: {cache_path} ({cache_data['count']} items, {cache_data['timestamp']})")
    return cache_data["data"]


def import_gym(client: httpx.Client, gym_summary) -> str:
    """Importe un gym."""
    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/gym",
        json={
            "stokt_id": MONTOBOARD_GYM_ID,
            "display_name": gym_summary.display_name,
            "location_string": gym_summary.location_string,
        }
    )
    response.raise_for_status()
    result = response.json()
    print(f"  Gym: {result['status']} (id={result['id']})")
    return result["id"]


def import_face(client: httpx.Client, face, gym_stokt_id: str) -> str:
    """Importe une face."""
    picture_path = face.picture.name if face.picture else ""
    picture_width = face.picture.width if face.picture else None
    picture_height = face.picture.height if face.picture else None

    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/face",
        json={
            "stokt_id": str(face.id),
            "gym_stokt_id": gym_stokt_id,
            "picture_path": picture_path,
            "picture_width": picture_width,
            "picture_height": picture_height,
            "feet_rules_options": face.feet_rules_options or [],
            "has_symmetry": face.has_symmetry,
        }
    )
    response.raise_for_status()
    result = response.json()
    print(f"  Face {face.id}: {result['status']}")
    return result["id"]


def import_holds(client: httpx.Client, holds: list, face_stokt_id: str) -> int:
    """Importe les holds d'une face (version legacy)."""
    count = 0
    for hold in holds:
        centroid = hold.centroid  # tuple (x, y)
        response = client.post(
            f"{MASTOC_API_URL}/api/sync/import/hold",
            json={
                "stokt_id": hold.id,
                "face_stokt_id": face_stokt_id,
                "polygon_str": hold.polygon_str,
                "centroid_x": centroid[0],
                "centroid_y": centroid[1],
                "area": hold.area,
                "path_str": hold.path_str,
            }
        )
        response.raise_for_status()
        count += 1
    return count


def import_holds_batch(client: httpx.Client, holds: list, face_stokt_id: str) -> tuple[int, int, int]:
    """Importe les holds d'une face en batch."""
    batch_data = []
    for hold in holds:
        centroid = hold.centroid
        batch_data.append({
            "stokt_id": hold.id,
            "face_stokt_id": face_stokt_id,
            "polygon_str": hold.polygon_str,
            "centroid_x": centroid[0],
            "centroid_y": centroid[1],
            "area": hold.area,
            "path_str": hold.path_str,
        })

    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/holds/batch",
        json={"holds": batch_data}
    )
    response.raise_for_status()
    result = response.json()
    return result["created"], result["updated"], result["errors"]


def import_user(client: httpx.Client, user_id: str, full_name: str) -> str:
    """Importe un user (setter)."""
    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/user",
        json={
            "stokt_id": user_id,
            "full_name": full_name,
        }
    )
    response.raise_for_status()
    return response.json()["id"]


def prepare_climb_data(climb) -> dict:
    """Prépare les données d'un climb pour l'import."""
    grade_font = climb.grade.font if climb.grade else None
    grade_ircra = climb.grade.ircra if climb.grade else None

    return {
        "stokt_id": str(climb.id),
        "face_stokt_id": str(climb.face_id),
        "setter_stokt_id": climb.setter.id if climb.setter else None,
        "name": climb.name,
        "holds_list": climb.holds_list,
        "grade_font": grade_font,
        "grade_ircra": grade_ircra,
        "feet_rule": climb.feet_rule,
        "description": None,
        "is_private": climb.is_private,
        "climbed_by": climb.climbed_by or 0,
        "total_likes": climb.total_likes or 0,
        "date_created": climb.date_created if climb.date_created else None,
    }


def import_users_batch(client: httpx.Client, climbs: list) -> tuple[int, int, int]:
    """Import les setters uniques par batch."""
    # Collecter les setters uniques
    setters = {}
    for climb in climbs:
        if climb.setter and climb.setter.id not in setters:
            setters[climb.setter.id] = climb.setter.full_name

    if not setters:
        return 0, 0, 0

    batch_data = [
        {"stokt_id": str(sid), "full_name": name}
        for sid, name in setters.items()
    ]

    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/users/batch",
        json={"users": batch_data}
    )
    response.raise_for_status()
    result = response.json()
    return result["created"], result["updated"], result["errors"]


def import_climbs_batch(client: httpx.Client, climbs: list, batch_size: int = 50):
    """Import les climbs par batch pour de meilleures performances."""
    total_created = 0
    total_updated = 0
    total_errors = 0

    # D'abord importer tous les setters en batch
    u_created, u_updated, u_errors = import_users_batch(client, climbs)
    print(f"  {u_created} setters créés, {u_updated} existants")

    # Ensuite importer les climbs par batch
    for i in range(0, len(climbs), batch_size):
        batch = climbs[i:i + batch_size]
        batch_data = [prepare_climb_data(c) for c in batch]

        response = client.post(
            f"{MASTOC_API_URL}/api/sync/import/climbs/batch",
            json={"climbs": batch_data}
        )
        response.raise_for_status()
        result = response.json()

        total_created += result["created"]
        total_updated += result["updated"]
        total_errors += result["errors"]

        print(f"  Batch {i // batch_size + 1}: +{result['created']} créés, {result['updated']} màj, {result['errors']} err")

    return total_created, total_updated, total_errors


def import_climb(client: httpx.Client, climb, face_stokt_id: str) -> str:
    """Importe un climb (version legacy, préférer import_climbs_batch)."""
    # Import du setter si présent
    setter_stokt_id = None
    if climb.setter:
        try:
            import_user(client, climb.setter.id, climb.setter.full_name)
            setter_stokt_id = climb.setter.id
        except Exception:
            pass  # Ignorer les erreurs de setter

    # Extraire grade si présent
    grade_font = climb.grade.font if climb.grade else None
    grade_ircra = climb.grade.ircra if climb.grade else None

    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/climb",
        json={
            "stokt_id": str(climb.id),
            "face_stokt_id": face_stokt_id,
            "setter_stokt_id": setter_stokt_id,
            "name": climb.name,
            "holds_list": climb.holds_list,  # String brute
            "grade_font": grade_font,
            "grade_ircra": grade_ircra,
            "feet_rule": climb.feet_rule,
            "description": None,  # Pas dans le modèle actuel
            "is_private": climb.is_private,
            "climbed_by": climb.climbed_by or 0,
            "total_likes": climb.total_likes or 0,
            "date_created": climb.date_created if climb.date_created else None,
        }
    )
    response.raise_for_status()
    return response.json()["status"]


def main():
    parser = argparse.ArgumentParser(description="Import Stokt data to mastoc-api")
    parser.add_argument("--username", help="Stokt username")
    parser.add_argument("--password", help="Stokt password")
    parser.add_argument("--token", help="Stokt token (alternative to username/password)")
    parser.add_argument("--api-key", help="mastoc-api API Key (if auth enabled)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually import")
    parser.add_argument("--batch", action="store_true", default=True, help="Use batch imports (default)")
    parser.add_argument("--no-batch", action="store_true", help="Disable batch imports (slow)")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for climbs (default: 50)")
    parser.add_argument("--use-cache", action="store_true", help="Use cached data instead of fetching from Stokt")
    parser.add_argument("--save-cache", action="store_true", help="Save fetched data to cache (for future --use-cache)")
    parser.add_argument("--climbs-only", action="store_true", help="Only import climbs (skip gym/faces/holds)")
    args = parser.parse_args()

    use_batch = args.batch and not args.no_batch

    # Si on utilise le cache, pas besoin de credentials Stokt
    if not args.use_cache and not args.token and not (args.username and args.password):
        parser.error("Either --token or --username/--password required (or use --use-cache)")

    # Client Stokt (sauf si cache-only)
    stokt = None
    if not args.use_cache or not args.climbs_only:
        print("=== Connexion à Stokt ===")
        stokt = StoktAPI()

        if args.token:
            stokt.set_token(args.token)
            print("Token configuré")
        elif args.username and args.password:
            stokt.login(args.username, args.password)
            print(f"Connecté en tant que {args.username}")
    else:
        print("=== Mode cache uniquement ===")

    # Client mastoc-api (avec API Key si fournie)
    headers = {}
    if args.api_key:
        headers[API_KEY_HEADER] = args.api_key
        print(f"API Key configurée")
    mastoc = httpx.Client(timeout=120, headers=headers)

    # Vérifier que mastoc-api est accessible
    print("\n=== Vérification mastoc-api ===")
    health = mastoc.get(f"{MASTOC_API_URL}/health").json()
    print(f"Status: {health['status']}, DB: {health['database']}")

    if args.dry_run:
        print("\n[DRY RUN] Aucune modification ne sera effectuée")

    if use_batch:
        print("\n[BATCH MODE] Import optimisé par lots")

    if not args.climbs_only:
        # 1. Import gym
        print("\n=== Import Gym Montoboard ===")
        gym_summary = stokt.get_gym_summary(MONTOBOARD_GYM_ID)
        print(f"Gym: {gym_summary.display_name}")

        if not args.dry_run:
            import_gym(mastoc, gym_summary)

        # 2. Import faces et holds
        print("\n=== Import Faces et Holds ===")
        walls = stokt.get_gym_walls(MONTOBOARD_GYM_ID)

        total_holds = 0
        for wall in walls:
            for face in wall.faces:
                print(f"\nFace {face.id}:")

                # Récupérer le setup complet avec holds
                face_setup = stokt.get_face_setup(face.id)
                print(f"  {len(face_setup.holds)} holds")

                if not args.dry_run:
                    import_face(mastoc, face_setup, MONTOBOARD_GYM_ID)

                    if use_batch:
                        created, updated, errors = import_holds_batch(mastoc, face_setup.holds, str(face.id))
                        print(f"  {created} créés, {updated} existants, {errors} erreurs")
                        total_holds += created
                    else:
                        count = import_holds(mastoc, face_setup.holds, str(face.id))
                        print(f"  {count} holds importés")
                        total_holds += count

        print(f"\nTotal: {total_holds} holds importés")
    else:
        print("\n[CLIMBS-ONLY] Skip gym/faces/holds")

    # 3. Import climbs
    print("\n=== Import Climbs ===")

    climbs = None
    if args.use_cache:
        climbs = load_from_cache("climbs")
        if climbs is None:
            print("  Pas de cache trouvé, récupération depuis Stokt...")

    if climbs is None:
        def progress_callback(current, total):
            print(f"  Récupération: {current}/{total}", end="\r")

        climbs = stokt.get_all_gym_climbs(MONTOBOARD_GYM_ID, callback=progress_callback)
        print(f"\n{len(climbs)} climbs récupérés depuis Stokt")

        if args.save_cache:
            save_to_cache("climbs", climbs)
    else:
        print(f"{len(climbs)} climbs depuis le cache")

    if not args.dry_run:
        if use_batch:
            created, updated, errors = import_climbs_batch(mastoc, climbs, args.batch_size)
            print(f"\nRésultat: {created} créés, {updated} mis à jour, {errors} erreurs")
        else:
            created = 0
            updated = 0
            errors = 0

            for i, climb in enumerate(climbs):
                try:
                    status = import_climb(mastoc, climb, str(climb.face_id))
                    if status == "created":
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors += 1
                    print(f"  Erreur climb {climb.id}: {e}")

                if (i + 1) % 50 == 0:
                    print(f"  Progress: {i + 1}/{len(climbs)} (created={created}, updated={updated}, errors={errors})")

            print(f"\nRésultat: {created} créés, {updated} mis à jour, {errors} erreurs")

    # Stats finales
    print("\n=== Stats finales ===")
    stats = mastoc.get(f"{MASTOC_API_URL}/api/sync/stats").json()
    print(f"  Gyms: {stats['gyms']}")
    print(f"  Faces: {stats['faces']}")
    print(f"  Holds: {stats['holds']}")
    print(f"  Climbs: {stats['climbs']}")
    print(f"  Users: {stats['users']}")

    print("\n=== Import terminé ===")


if __name__ == "__main__":
    main()

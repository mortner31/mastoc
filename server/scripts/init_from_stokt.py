#!/usr/bin/env python3
"""
Script d'import initial des données Stokt vers mastoc-api.

Usage:
    python scripts/init_from_stokt.py --username USER --password PASS

Ou avec token existant:
    python scripts/init_from_stokt.py --token TOKEN
"""

import argparse
import sys
from pathlib import Path

# Ajouter le chemin du client mastoc
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mastoc" / "src"))

import httpx
from mastoc.api.client import StoktAPI, MONTOBOARD_GYM_ID


# Configuration
MASTOC_API_URL = "https://mastoc-production.up.railway.app"


def import_gym(client: httpx.Client, gym_summary) -> str:
    """Importe un gym."""
    response = client.post(
        f"{MASTOC_API_URL}/api/sync/import/gym",
        params={
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
    """Importe les holds d'une face."""
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


def import_climb(client: httpx.Client, climb, face_stokt_id: str) -> str:
    """Importe un climb."""
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
    parser.add_argument("--dry-run", action="store_true", help="Don't actually import")
    args = parser.parse_args()

    if not args.token and not (args.username and args.password):
        parser.error("Either --token or --username/--password required")

    # Client Stokt
    print("=== Connexion à Stokt ===")
    stokt = StoktAPI()

    if args.token:
        stokt.set_token(args.token)
        print("Token configuré")
    else:
        stokt.login(args.username, args.password)
        print(f"Connecté en tant que {args.username}")

    # Client mastoc-api
    mastoc = httpx.Client(timeout=60)

    # Vérifier que mastoc-api est accessible
    print("\n=== Vérification mastoc-api ===")
    health = mastoc.get(f"{MASTOC_API_URL}/health").json()
    print(f"Status: {health['status']}, DB: {health['database']}")

    if args.dry_run:
        print("\n[DRY RUN] Aucune modification ne sera effectuée")

    # 1. Import gym
    print("\n=== Import Gym Montoboard ===")
    gym_summary = stokt.get_gym_summary(MONTOBOARD_GYM_ID)
    print(f"Gym: {gym_summary.display_name}")

    if not args.dry_run:
        import_gym(mastoc, gym_summary)

    # 2. Import faces et holds
    print("\n=== Import Faces et Holds ===")
    walls = stokt.get_gym_walls(MONTOBOARD_GYM_ID)

    face_ids = []
    for wall in walls:
        for face in wall.faces:
            face_ids.append(face.id)
            print(f"\nFace {face.id}:")

            # Récupérer le setup complet avec holds
            face_setup = stokt.get_face_setup(face.id)
            print(f"  {len(face_setup.holds)} holds")

            if not args.dry_run:
                import_face(mastoc, face_setup, MONTOBOARD_GYM_ID)
                count = import_holds(mastoc, face_setup.holds, str(face.id))
                print(f"  {count} holds importés")

    # 3. Import climbs
    print("\n=== Import Climbs ===")

    def progress_callback(current, total):
        print(f"  Récupération: {current}/{total}", end="\r")

    climbs = stokt.get_all_gym_climbs(MONTOBOARD_GYM_ID, callback=progress_callback)
    print(f"\n{len(climbs)} climbs récupérés")

    if not args.dry_run:
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

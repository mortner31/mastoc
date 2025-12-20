"""
Script d'extraction de tous les climbs d'un gym Stokt

Exporte les données en JSON pour analyse ultérieure.
"""

import json
import os
from datetime import datetime
from stokt_api import StoktAPI, MONTOBOARD_GYM_ID, parse_holds_list


def extract_all_climbs(api: StoktAPI, gym_id: str, max_age: int = 365) -> dict:
    """
    Extrait toutes les données d'un gym

    Returns:
        Dict avec gym_summary, walls, climbs
    """
    data = {
        "extracted_at": datetime.now().isoformat(),
        "gym_id": gym_id,
        "gym_summary": None,
        "walls": [],
        "recent_climbs": [],
        "my_sent_climbs": []
    }

    # 1. Récupérer le résumé du gym
    print("Récupération du résumé du gym...")
    data["gym_summary"] = api.get_gym_summary(gym_id)
    print(f"  Gym: {data['gym_summary']['displayName']}")
    print(f"  Total climbs: {data['gym_summary']['numberOfClimbs']}")

    # 2. Récupérer les walls et faces
    print("\nRécupération des walls...")
    data["walls"] = api.get_gym_walls(gym_id)
    for wall in data["walls"]:
        print(f"  Wall: {wall['name']}")
        for face in wall.get('faces', []):
            print(f"    Face: {face['id']} - {face['totalClimbs']} climbs")

    # 3. Récupérer tous les climbs récents
    print(f"\nRécupération des climbs (max_age={max_age} jours)...")
    climbs_response = api.get_gym_climbs(gym_id, max_age=max_age)
    data["recent_climbs"] = climbs_response.get("results", [])
    print(f"  Climbs récupérés: {len(data['recent_climbs'])}")

    # Pagination si nécessaire
    next_url = climbs_response.get("next")
    while next_url:
        print(f"  Pagination: récupération page suivante...")
        response = api.session.get(next_url, headers=api._auth_headers())
        response.raise_for_status()
        page_data = response.json()
        data["recent_climbs"].extend(page_data.get("results", []))
        next_url = page_data.get("next")
        print(f"  Total: {len(data['recent_climbs'])} climbs")

    # 4. Récupérer mes climbs validés
    print("\nRécupération de mes climbs validés...")
    data["my_sent_climbs"] = api.get_my_sent_climbs(gym_id)
    print(f"  Mes climbs: {len(data['my_sent_climbs'])}")

    return data


def analyze_climbs(climbs: list) -> dict:
    """Analyse statistique des climbs"""
    stats = {
        "total": len(climbs),
        "grades": {},
        "setters": {},
        "feet_rules": {}
    }

    for climb in climbs:
        # Grades
        grade = climb.get("crowdGrade", {}).get("font", "Unknown")
        stats["grades"][grade] = stats["grades"].get(grade, 0) + 1

        # Setters
        setter = climb.get("climbSetters", {}).get("fullName", "Unknown")
        stats["setters"][setter] = stats["setters"].get(setter, 0) + 1

        # Feet rules
        feet = climb.get("feetRule", "Unknown")
        stats["feet_rules"][feet] = stats["feet_rules"].get(feet, 0) + 1

    return stats


def main():
    # Configuration
    TOKEN = "dba723cbee34ff3cf049b12150a21dc8919c3cf8"
    OUTPUT_DIR = "extracted/data"

    # Créer le dossier de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialiser l'API
    api = StoktAPI()
    api.set_token(TOKEN)

    # Extraire toutes les données
    print("=" * 50)
    print("EXTRACTION DES DONNÉES STOKT")
    print("=" * 50)

    data = extract_all_climbs(api, MONTOBOARD_GYM_ID, max_age=365)

    # Sauvegarder en JSON
    output_file = os.path.join(OUTPUT_DIR, f"montoboard_{datetime.now().strftime('%Y%m%d')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nDonnées sauvegardées: {output_file}")

    # Analyser les climbs
    print("\n" + "=" * 50)
    print("STATISTIQUES")
    print("=" * 50)

    stats = analyze_climbs(data["recent_climbs"])
    print(f"\nTotal climbs: {stats['total']}")

    print("\nRépartition par grade (Font):")
    for grade, count in sorted(stats["grades"].items()):
        print(f"  {grade}: {count}")

    print("\nTop 5 setters:")
    top_setters = sorted(stats["setters"].items(), key=lambda x: x[1], reverse=True)[:5]
    for setter, count in top_setters:
        print(f"  {setter}: {count}")

    print("\nRègles de pieds:")
    for rule, count in sorted(stats["feet_rules"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {rule}: {count}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script de test pour les endpoints sociaux de l'API Stokt.

Usage:
    python -m mastoc.tools.test_social_endpoints

Ce script teste les endpoints :
- GET api/climbs/{id}/latest-sends
- GET api/climbs/{id}/comments
- GET api/climbs/{id}/likes
- GET api/gyms/{id}/my-bookmarked-climbs
- GET api/gyms/{id}/my-liked-climbs
"""

import sys
from getpass import getpass

from mastoc.api.client import StoktAPI, MONTOBOARD_GYM_ID, AuthenticationError


def test_endpoints(api: StoktAPI, climb_id: str):
    """Teste les endpoints sociaux sur un climb spécifique."""

    print(f"\n{'='*60}")
    print(f"Test des endpoints sociaux pour climb: {climb_id[:8]}...")
    print('='*60)

    # 1. Test latest-sends
    print("\n[1/5] GET api/climbs/{id}/latest-sends")
    try:
        sends = api.get_climb_sends(climb_id, limit=5)
        print(f"  ✓ {len(sends)} ascensions récupérées")
        for s in sends[:3]:
            flash = "⚡" if s.is_flash else ""
            print(f"    - {s.user.full_name} {flash} ({s.date[:10]})")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

    # 2. Test comments
    print("\n[2/5] GET api/climbs/{id}/comments")
    try:
        comments = api.get_climb_comments(climb_id, limit=5)
        print(f"  ✓ {len(comments)} commentaires récupérés")
        for c in comments[:3]:
            text = c.text[:50] + "..." if len(c.text) > 50 else c.text
            print(f"    - {c.user.full_name}: {text}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

    # 3. Test likes
    print("\n[3/5] GET api/climbs/{id}/likes")
    try:
        likes = api.get_climb_likes(climb_id)
        print(f"  ✓ {len(likes)} likes récupérés")
        for lk in likes[:3]:
            print(f"    - {lk.user.full_name}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

    # 4. Test my-bookmarked-climbs
    print("\n[4/5] GET api/gyms/{id}/my-bookmarked-climbs")
    try:
        bookmarks = api.get_my_bookmarked_climbs(MONTOBOARD_GYM_ID)
        print(f"  ✓ {len(bookmarks)} climbs favoris")
        for b in bookmarks[:3]:
            print(f"    - {b.name} ({b.grade.font if b.grade else '?'})")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

    # 5. Test my-liked-climbs
    print("\n[5/5] GET api/gyms/{id}/my-liked-climbs")
    try:
        liked = api.get_my_liked_climbs(MONTOBOARD_GYM_ID)
        print(f"  ✓ {len(liked)} climbs likés")
        for lc in liked[:3]:
            print(f"    - {lc.name} ({lc.grade.font if lc.grade else '?'})")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

    print(f"\n{'='*60}")
    print("Tests terminés")
    print('='*60)


def main():
    api = StoktAPI()

    print("=" * 60)
    print("Test des endpoints sociaux Stokt")
    print("=" * 60)

    # Demander le token ou les credentials
    print("\nAuthentification requise.")
    print("Options:")
    print("  1. Entrer un token existant")
    print("  2. Se connecter avec email/mot de passe")

    choice = input("\nChoix (1 ou 2): ").strip()

    if choice == "1":
        token = input("Token: ").strip()
        if not token:
            print("Token vide, abandon.")
            return 1
        api.set_token(token)
    elif choice == "2":
        email = input("Email: ").strip()
        password = getpass("Mot de passe: ")
        try:
            result = api.login(email, password)
            print(f"✓ Connecté en tant que {result.get('user', {}).get('fullName', 'inconnu')}")
            print(f"  Token: {api.token[:20]}...")
        except Exception as e:
            print(f"✗ Erreur de connexion: {e}")
            return 1
    else:
        print("Choix invalide, abandon.")
        return 1

    # Vérifier l'authentification
    try:
        profile = api.get_user_profile()
        print(f"✓ Authentification valide: {profile.get('fullName', 'inconnu')}")
    except AuthenticationError:
        print("✗ Token invalide")
        return 1

    # Récupérer un climb pour tester
    print("\nRécupération d'un climb avec commentaires...")
    climbs, total, _ = api.get_gym_climbs(MONTOBOARD_GYM_ID, max_age=30)

    # Chercher un climb avec des commentaires
    test_climb = None
    for climb in climbs:
        if climb.total_comments > 0:
            test_climb = climb
            break

    if not test_climb and climbs:
        test_climb = climbs[0]

    if not test_climb:
        print("✗ Aucun climb trouvé pour les tests")
        return 1

    print(f"  Climb sélectionné: {test_climb.name}")
    print(f"  - {test_climb.climbed_by} ascensions")
    print(f"  - {test_climb.total_likes} likes")
    print(f"  - {test_climb.total_comments} commentaires")

    # Lancer les tests
    test_endpoints(api, test_climb.id)

    return 0


if __name__ == "__main__":
    sys.exit(main())

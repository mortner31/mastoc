"""
CLI pour afficher l'état de synchronisation.

Usage:
    python -m mastoc.tools.sync_status
"""

import sys
from mastoc.core.sync_stats import get_sync_stats, get_local_climbs, SyncStats, LocalClimb


def print_stats(stats: SyncStats):
    """Affiche les statistiques de sync."""
    print("=" * 50)
    print("       État Synchronisation mastoc")
    print("=" * 50)
    print()
    print(f"Climbs :")
    print(f"  Total         : {stats.total_climbs}")
    print(f"  Synchronisés  : {stats.synced_climbs} ({stats.sync_percentage:.1f}%)")
    print(f"  Locaux        : {stats.local_climbs}")
    print()
    print(f"Autres :")
    print(f"  Prises        : {stats.total_holds}")
    print(f"  Utilisateurs  : {stats.total_users}")
    print()


def print_local_climbs(climbs: list[LocalClimb]):
    """Affiche la liste des climbs locaux."""
    if not climbs:
        print("Aucun climb local (tous synchronisés avec Stokt)")
        return

    print(f"Climbs locaux ({len(climbs)}) :")
    print("-" * 50)
    for c in climbs:
        grade = c.grade or "?"
        setter = c.setter_name or "inconnu"
        created = c.created_at[:10] if c.created_at else "?"
        print(f"  • {c.name} ({grade}) - par {setter} - {created}")


def main():
    """Point d'entrée CLI."""
    print("Connexion à Railway...")
    print()

    try:
        stats = get_sync_stats()
        print_stats(stats)

        if stats.local_climbs > 0:
            local = get_local_climbs()
            print_local_climbs(local)

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

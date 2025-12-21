"""
Gestion de la base de données SQLite pour mastock.

Stocke les climbs, prises et métadonnées de synchronisation.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, Iterator

# Chemin par défaut de la base de données
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "mastock.db"

# Version du schéma pour les migrations futures
SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Table de métadonnées (version schéma, dernière sync, etc.)
CREATE TABLE IF NOT EXISTS sync_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Table des faces (murs)
CREATE TABLE IF NOT EXISTS faces (
    id TEXT PRIMARY KEY,
    gym TEXT NOT NULL,
    wall TEXT NOT NULL,
    picture_name TEXT,
    picture_width INTEGER,
    picture_height INTEGER,
    feet_rules_options TEXT,  -- JSON array
    has_symmetry INTEGER DEFAULT 0,
    total_climbs INTEGER DEFAULT 0,
    updated_at TEXT NOT NULL
);

-- Table des prises (holds)
CREATE TABLE IF NOT EXISTS holds (
    id INTEGER PRIMARY KEY,
    face_id TEXT NOT NULL,
    area REAL,
    polygon_str TEXT NOT NULL,
    touch_polygon_str TEXT,
    path_str TEXT,
    centroid_x REAL,
    centroid_y REAL,
    top_polygon_str TEXT,
    center_tape_str TEXT,
    right_tape_str TEXT,
    left_tape_str TEXT,
    FOREIGN KEY (face_id) REFERENCES faces(id)
);

-- Index pour recherche rapide des prises par face
CREATE INDEX IF NOT EXISTS idx_holds_face_id ON holds(face_id);

-- Table des setters (créateurs de climbs)
CREATE TABLE IF NOT EXISTS setters (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    avatar TEXT
);

-- Table des climbs
CREATE TABLE IF NOT EXISTS climbs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    holds_list TEXT NOT NULL,
    mirror_holds_list TEXT,
    feet_rule TEXT,
    face_id TEXT NOT NULL,
    wall_id TEXT,
    wall_name TEXT,
    setter_id TEXT,
    date_created TEXT,
    is_private INTEGER DEFAULT 0,
    is_benchmark INTEGER DEFAULT 0,
    climbed_by INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    has_symmetric INTEGER DEFAULT 0,
    angle TEXT,
    is_angle_adjustable INTEGER DEFAULT 0,
    circuit TEXT,
    tags TEXT,
    grade_ircra REAL,
    grade_hueco TEXT,
    grade_font TEXT,
    grade_dankyu TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (face_id) REFERENCES faces(id),
    FOREIGN KEY (setter_id) REFERENCES setters(id)
);

-- Index pour filtres fréquents
CREATE INDEX IF NOT EXISTS idx_climbs_face_id ON climbs(face_id);
CREATE INDEX IF NOT EXISTS idx_climbs_setter_id ON climbs(setter_id);
CREATE INDEX IF NOT EXISTS idx_climbs_grade_font ON climbs(grade_font);
CREATE INDEX IF NOT EXISTS idx_climbs_date_created ON climbs(date_created);

-- Table de liaison climb <-> hold pour recherche par prises
CREATE TABLE IF NOT EXISTS climb_holds (
    climb_id TEXT NOT NULL,
    hold_id INTEGER NOT NULL,
    hold_type TEXT NOT NULL,  -- S, O, F, T
    PRIMARY KEY (climb_id, hold_id, hold_type),
    FOREIGN KEY (climb_id) REFERENCES climbs(id),
    FOREIGN KEY (hold_id) REFERENCES holds(id)
);

-- Index pour recherche de climbs par prise
CREATE INDEX IF NOT EXISTS idx_climb_holds_hold_id ON climb_holds(hold_id);
"""


class Database:
    """Gestionnaire de base de données SQLite pour mastock."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialise la connexion à la base de données.

        Args:
            db_path: Chemin de la base de données. Utilise le chemin par défaut si None.
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Crée les tables si elles n'existent pas."""
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)

            # Vérifier/initialiser la version du schéma
            cursor = conn.execute(
                "SELECT value FROM sync_metadata WHERE key = 'schema_version'"
            )
            row = cursor.fetchone()

            if row is None:
                now = datetime.now().isoformat()
                conn.execute(
                    "INSERT INTO sync_metadata (key, value, updated_at) VALUES (?, ?, ?)",
                    ("schema_version", str(SCHEMA_VERSION), now)
                )

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager pour obtenir une connexion."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_metadata(self, key: str) -> Optional[str]:
        """Récupère une valeur de métadonnée."""
        with self.connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM sync_metadata WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            return row["value"] if row else None

    def set_metadata(self, key: str, value: str):
        """Définit une valeur de métadonnée."""
        now = datetime.now().isoformat()
        with self.connection() as conn:
            conn.execute(
                """INSERT INTO sync_metadata (key, value, updated_at)
                   VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = ?""",
                (key, value, now, value, now)
            )

    def get_last_sync(self) -> Optional[datetime]:
        """Récupère la date de dernière synchronisation."""
        value = self.get_metadata("last_sync")
        return datetime.fromisoformat(value) if value else None

    def set_last_sync(self, dt: Optional[datetime] = None):
        """Définit la date de dernière synchronisation."""
        dt = dt or datetime.now()
        self.set_metadata("last_sync", dt.isoformat())

    def get_climb_count(self) -> int:
        """Retourne le nombre de climbs en base."""
        with self.connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM climbs")
            return cursor.fetchone()[0]

    def get_hold_count(self) -> int:
        """Retourne le nombre de prises en base."""
        with self.connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM holds")
            return cursor.fetchone()[0]

    def clear_all(self):
        """Supprime toutes les données (pour réimport complet)."""
        with self.connection() as conn:
            conn.execute("DELETE FROM climb_holds")
            conn.execute("DELETE FROM climbs")
            conn.execute("DELETE FROM holds")
            conn.execute("DELETE FROM faces")
            conn.execute("DELETE FROM setters")
            conn.execute("DELETE FROM sync_metadata WHERE key != 'schema_version'")

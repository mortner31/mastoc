"""
Repository pour les opérations CRUD sur la base de données.

Gère l'import/export des données entre API et SQLite.
"""

import json
from datetime import datetime
from typing import Optional

from mastoc.api.models import Climb, Hold, Face, HoldType
from mastoc.db.database import Database


class ClimbRepository:
    """Repository pour les climbs."""

    def __init__(self, db: Database):
        self.db = db

    def save_climb(self, climb: Climb):
        """Sauvegarde un climb en base."""
        now = datetime.now().isoformat()

        with self.db.connection() as conn:
            # Sauvegarder le setter si présent
            setter_id = None
            if climb.setter:
                conn.execute(
                    """INSERT INTO setters (id, full_name, avatar)
                       VALUES (?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET full_name = ?, avatar = ?""",
                    (climb.setter.id, climb.setter.full_name, climb.setter.avatar,
                     climb.setter.full_name, climb.setter.avatar)
                )
                setter_id = climb.setter.id

            # Sauvegarder le climb
            conn.execute(
                """INSERT INTO climbs (
                       id, name, holds_list, mirror_holds_list, feet_rule,
                       face_id, wall_id, wall_name, setter_id, date_created,
                       is_private, is_benchmark, climbed_by, total_likes,
                       total_comments, has_symmetric, angle, is_angle_adjustable,
                       circuit, tags, grade_ircra, grade_hueco, grade_font,
                       grade_dankyu, updated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                       name = ?, holds_list = ?, climbed_by = ?, total_likes = ?,
                       total_comments = ?, updated_at = ?""",
                (climb.id, climb.name, climb.holds_list, climb.mirror_holds_list,
                 climb.feet_rule, climb.face_id, climb.wall_id, climb.wall_name,
                 setter_id, climb.date_created, climb.is_private, climb.is_benchmark,
                 climb.climbed_by, climb.total_likes, climb.total_comments,
                 climb.has_symmetric, climb.angle, climb.is_angle_adjustable,
                 climb.circuit, climb.tags,
                 climb.grade.ircra if climb.grade else None,
                 climb.grade.hueco if climb.grade else None,
                 climb.grade.font if climb.grade else None,
                 climb.grade.dankyu if climb.grade else None,
                 now,
                 # ON CONFLICT updates
                 climb.name, climb.holds_list, climb.climbed_by, climb.total_likes,
                 climb.total_comments, now)
            )

            # Sauvegarder les liens climb <-> holds
            conn.execute("DELETE FROM climb_holds WHERE climb_id = ?", (climb.id,))
            for ch in climb.get_holds():
                conn.execute(
                    "INSERT OR IGNORE INTO climb_holds (climb_id, hold_id, hold_type) VALUES (?, ?, ?)",
                    (climb.id, ch.hold_id, ch.hold_type.value)
                )

    def save_climbs(self, climbs: list[Climb], callback=None):
        """Sauvegarde plusieurs climbs en base."""
        total = len(climbs)
        for i, climb in enumerate(climbs):
            self.save_climb(climb)
            if callback and (i + 1) % 100 == 0:
                callback(i + 1, total)
        if callback:
            callback(total, total)

    def get_climb(self, climb_id: str) -> Optional[Climb]:
        """Récupère un climb par son ID."""
        with self.db.connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM climbs WHERE id = ?", (climb_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_climb(dict(row))

    def get_all_climbs(self) -> list[Climb]:
        """Récupère tous les climbs."""
        with self.db.connection() as conn:
            cursor = conn.execute("SELECT * FROM climbs ORDER BY date_created DESC")
            return [self._row_to_climb(dict(row)) for row in cursor.fetchall()]

    def get_climbs_by_grade(self, grade_font: str) -> list[Climb]:
        """Récupère les climbs par grade Fontainebleau."""
        with self.db.connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM climbs WHERE grade_font = ? ORDER BY date_created DESC",
                (grade_font,)
            )
            return [self._row_to_climb(dict(row)) for row in cursor.fetchall()]

    def get_climbs_by_hold(self, hold_id: int) -> list[Climb]:
        """Récupère les climbs utilisant une prise spécifique."""
        with self.db.connection() as conn:
            cursor = conn.execute(
                """SELECT c.* FROM climbs c
                   JOIN climb_holds ch ON c.id = ch.climb_id
                   WHERE ch.hold_id = ?
                   ORDER BY c.date_created DESC""",
                (hold_id,)
            )
            return [self._row_to_climb(dict(row)) for row in cursor.fetchall()]

    def get_climbs_by_holds(self, hold_ids: list[int]) -> list[Climb]:
        """Récupère les climbs utilisant TOUTES les prises spécifiées."""
        if not hold_ids:
            return []

        placeholders = ",".join("?" * len(hold_ids))
        with self.db.connection() as conn:
            cursor = conn.execute(
                f"""SELECT c.* FROM climbs c
                    JOIN climb_holds ch ON c.id = ch.climb_id
                    WHERE ch.hold_id IN ({placeholders})
                    GROUP BY c.id
                    HAVING COUNT(DISTINCT ch.hold_id) = ?
                    ORDER BY c.date_created DESC""",
                (*hold_ids, len(hold_ids))
            )
            return [self._row_to_climb(dict(row)) for row in cursor.fetchall()]

    def get_unique_grades(self) -> list[str]:
        """Récupère la liste des grades uniques."""
        with self.db.connection() as conn:
            cursor = conn.execute(
                "SELECT DISTINCT grade_font FROM climbs WHERE grade_font IS NOT NULL ORDER BY grade_ircra"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_unique_setters(self) -> list[tuple[str, str]]:
        """Récupère la liste des setters uniques (id, nom)."""
        with self.db.connection() as conn:
            cursor = conn.execute(
                "SELECT id, full_name FROM setters ORDER BY full_name"
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]

    def _row_to_climb(self, row: dict) -> Climb:
        """Convertit une ligne SQLite en Climb."""
        from mastoc.api.models import ClimbSetter, Grade

        setter = None
        if row.get("setter_id"):
            with self.db.connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM setters WHERE id = ?", (row["setter_id"],)
                )
                setter_row = cursor.fetchone()
                if setter_row:
                    setter = ClimbSetter(
                        id=setter_row["id"],
                        full_name=setter_row["full_name"],
                        avatar=setter_row["avatar"]
                    )

        grade = None
        if row.get("grade_font"):
            grade = Grade(
                ircra=row.get("grade_ircra") or 0,
                hueco=row.get("grade_hueco") or "",
                font=row.get("grade_font") or "",
                dankyu=row.get("grade_dankyu") or ""
            )

        return Climb(
            id=row["id"],
            name=row["name"],
            holds_list=row["holds_list"],
            mirror_holds_list=row.get("mirror_holds_list") or "",
            feet_rule=row.get("feet_rule") or "",
            face_id=row["face_id"],
            wall_id=row.get("wall_id") or "",
            wall_name=row.get("wall_name") or "",
            date_created=row.get("date_created") or "",
            is_private=bool(row.get("is_private")),
            is_benchmark=bool(row.get("is_benchmark")),
            climbed_by=row.get("climbed_by") or 0,
            total_likes=row.get("total_likes") or 0,
            total_comments=row.get("total_comments") or 0,
            has_symmetric=bool(row.get("has_symmetric")),
            angle=row.get("angle") or "",
            is_angle_adjustable=bool(row.get("is_angle_adjustable")),
            circuit=row.get("circuit") or "",
            tags=row.get("tags") or "",
            setter=setter,
            grade=grade,
        )


class HoldRepository:
    """Repository pour les prises."""

    def __init__(self, db: Database):
        self.db = db

    def save_face(self, face: Face):
        """Sauvegarde une face et ses prises en base."""
        now = datetime.now().isoformat()

        with self.db.connection() as conn:
            # Sauvegarder la face
            conn.execute(
                """INSERT INTO faces (
                       id, gym, wall, picture_name, picture_width, picture_height,
                       feet_rules_options, has_symmetry, total_climbs, updated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                       gym = ?, wall = ?, picture_name = ?, picture_width = ?,
                       picture_height = ?, feet_rules_options = ?, total_climbs = ?,
                       updated_at = ?""",
                (face.id, face.gym, face.wall,
                 face.picture.name if face.picture else None,
                 face.picture.width if face.picture else None,
                 face.picture.height if face.picture else None,
                 json.dumps(face.feet_rules_options),
                 face.has_symmetry, face.total_climbs, now,
                 # ON CONFLICT updates
                 face.gym, face.wall,
                 face.picture.name if face.picture else None,
                 face.picture.width if face.picture else None,
                 face.picture.height if face.picture else None,
                 json.dumps(face.feet_rules_options), face.total_climbs, now)
            )

            # Sauvegarder les prises
            for hold in face.holds:
                cx, cy = hold.centroid
                conn.execute(
                    """INSERT INTO holds (
                           id, face_id, area, polygon_str, touch_polygon_str, path_str,
                           centroid_x, centroid_y, top_polygon_str, center_tape_str,
                           right_tape_str, left_tape_str
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET
                           polygon_str = ?, centroid_x = ?, centroid_y = ?""",
                    (hold.id, face.id, hold.area, hold.polygon_str,
                     hold.touch_polygon_str, hold.path_str, cx, cy,
                     hold.top_polygon_str, hold.center_tape_str,
                     hold.right_tape_str, hold.left_tape_str,
                     # ON CONFLICT updates
                     hold.polygon_str, cx, cy)
                )

    def save_hold(self, hold: Hold, face_id: str):
        """Sauvegarde une prise individuelle en base."""
        with self.db.connection() as conn:
            cx, cy = hold.centroid
            conn.execute(
                """INSERT INTO holds (
                       id, face_id, area, polygon_str, touch_polygon_str, path_str,
                       centroid_x, centroid_y, top_polygon_str, center_tape_str,
                       right_tape_str, left_tape_str
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                       face_id = ?, polygon_str = ?, centroid_x = ?, centroid_y = ?,
                       center_tape_str = ?, right_tape_str = ?, left_tape_str = ?""",
                (hold.id, face_id, hold.area, hold.polygon_str,
                 hold.touch_polygon_str, hold.path_str, cx, cy,
                 hold.top_polygon_str, hold.center_tape_str,
                 hold.right_tape_str, hold.left_tape_str,
                 # ON CONFLICT updates
                 face_id, hold.polygon_str, cx, cy,
                 hold.center_tape_str, hold.right_tape_str, hold.left_tape_str)
            )

    def get_hold(self, hold_id: int) -> Optional[Hold]:
        """Récupère une prise par son ID."""
        with self.db.connection() as conn:
            cursor = conn.execute("SELECT * FROM holds WHERE id = ?", (hold_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_hold(dict(row))

    def get_all_holds(self, face_id: Optional[str] = None) -> list[Hold]:
        """Récupère toutes les prises, optionnellement filtrées par face."""
        with self.db.connection() as conn:
            if face_id:
                cursor = conn.execute(
                    "SELECT * FROM holds WHERE face_id = ?", (face_id,)
                )
            else:
                cursor = conn.execute("SELECT * FROM holds")
            return [self._row_to_hold(dict(row)) for row in cursor.fetchall()]

    def get_face(self, face_id: str) -> Optional[Face]:
        """Récupère une face par son ID."""
        with self.db.connection() as conn:
            cursor = conn.execute("SELECT * FROM faces WHERE id = ?", (face_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_face(dict(row))

    def _row_to_hold(self, row: dict) -> Hold:
        """Convertit une ligne SQLite en Hold."""
        centroid_str = f"{row['centroid_x']} {row['centroid_y']}"
        return Hold(
            id=row["id"],
            area=row.get("area") or 0,
            polygon_str=row["polygon_str"],
            touch_polygon_str=row.get("touch_polygon_str") or "",
            path_str=row.get("path_str") or "",
            centroid_str=centroid_str,
            top_polygon_str=row.get("top_polygon_str") or "",
            center_tape_str=row.get("center_tape_str") or "",
            right_tape_str=row.get("right_tape_str") or "",
            left_tape_str=row.get("left_tape_str") or "",
        )

    def _row_to_face(self, row: dict) -> Face:
        """Convertit une ligne SQLite en Face."""
        from mastoc.api.models import FacePicture

        picture = None
        if row.get("picture_name"):
            picture = FacePicture(
                name=row["picture_name"],
                width=row.get("picture_width") or 0,
                height=row.get("picture_height") or 0
            )

        feet_rules = []
        if row.get("feet_rules_options"):
            feet_rules = json.loads(row["feet_rules_options"])

        # Charger les prises associées
        holds = self.get_all_holds(row["id"])

        return Face(
            id=row["id"],
            gym=row.get("gym") or "",
            wall=row.get("wall") or "",
            is_active=True,
            total_climbs=row.get("total_climbs") or 0,
            picture=picture,
            feet_rules_options=feet_rules,
            has_symmetry=bool(row.get("has_symmetry")),
            holds=holds,
        )

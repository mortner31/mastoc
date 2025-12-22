"""
Double slider pour la sélection de plage de niveau.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt, pyqtSignal


# Grades Fontainebleau avec valeurs IRCRA correspondantes (valeurs réelles de la DB)
# Note: chaque grade a une plage IRCRA, on utilise la borne inférieure
FONT_GRADES = [
    ('4', 12.0),    # 12.0 - 13.12
    ('4+', 13.25),  # 13.25 - 14.12
    ('5', 14.25),   # 14.25 - 14.88
    ('5+', 15.0),   # 15.0 - 15.25
    ('6A', 15.5),   # 15.5 - 16.25
    ('6A+', 16.5),  # 16.5 - 17.25
    ('6B', 17.5),   # 17.5 - 17.75
    ('6B+', 18.0),  # 18.0 - 18.25
    ('6C', 18.5),   # 18.5 - 19.25
    ('6C+', 19.5),  # 19.5 - 20.0
    ('7A', 20.5),   # 20.5 - 21.25
    ('7A+', 21.5),  # 21.5 - 22.0
    ('7B', 22.5),   # 22.5 - 23.0
    ('7B+', 23.5),  # 23.5
    ('7C', 24.5),   # 24.5
    ('8A', 26.5),   # 26.5
]


def grade_to_index(grade_font: str) -> int:
    """Convertit un grade Font en index."""
    for i, (g, _) in enumerate(FONT_GRADES):
        if g == grade_font:
            return i
    return 0


def index_to_grade(index: int) -> tuple[str, float]:
    """Convertit un index en grade (font, ircra)."""
    if 0 <= index < len(FONT_GRADES):
        return FONT_GRADES[index]
    return FONT_GRADES[0]


def ircra_to_index(ircra: float) -> int:
    """Trouve l'index le plus proche pour une valeur IRCRA."""
    for i, (_, val) in enumerate(FONT_GRADES):
        if ircra <= val:
            return i
    return len(FONT_GRADES) - 1


class LevelRangeSlider(QWidget):
    """Double slider pour sélectionner une plage de niveau."""

    range_changed = pyqtSignal(float, float)  # Émet (min_ircra, max_ircra)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_index = 0
        self.max_index = len(FONT_GRADES) - 1

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Titre
        title = QLabel("Plage de niveau")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        # Slider minimum
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("Min:"))
        self.min_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_slider.setRange(0, len(FONT_GRADES) - 1)
        self.min_slider.setValue(0)
        self.min_slider.valueChanged.connect(self.on_min_changed)
        min_layout.addWidget(self.min_slider)
        self.min_label = QLabel("4")
        self.min_label.setMinimumWidth(40)
        min_layout.addWidget(self.min_label)
        layout.addLayout(min_layout)

        # Slider maximum
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Max:"))
        self.max_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_slider.setRange(0, len(FONT_GRADES) - 1)
        self.max_slider.setValue(len(FONT_GRADES) - 1)
        self.max_slider.valueChanged.connect(self.on_max_changed)
        max_layout.addWidget(self.max_slider)
        self.max_label = QLabel("8A")
        self.max_label.setMinimumWidth(40)
        max_layout.addWidget(self.max_label)
        layout.addLayout(max_layout)

        # Affichage de la plage
        self.range_label = QLabel("4 - 8A")
        self.range_label.setStyleSheet("font-size: 14px; color: #666;")
        self.range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.range_label)

    def on_min_changed(self, value: int):
        """Appelé quand le slider min change."""
        if value > self.max_index:
            self.min_slider.setValue(self.max_index)
            return

        self.min_index = value
        grade, _ = index_to_grade(value)
        self.min_label.setText(grade)
        self.update_range_label()
        self.emit_range()

    def on_max_changed(self, value: int):
        """Appelé quand le slider max change."""
        if value < self.min_index:
            self.max_slider.setValue(self.min_index)
            return

        self.max_index = value
        grade, _ = index_to_grade(value)
        self.max_label.setText(grade)
        self.update_range_label()
        self.emit_range()

    def update_range_label(self):
        """Met à jour l'affichage de la plage."""
        min_grade, _ = index_to_grade(self.min_index)
        max_grade, _ = index_to_grade(self.max_index)
        self.range_label.setText(f"{min_grade} - {max_grade}")

    def emit_range(self):
        """Émet le signal range_changed."""
        _, min_ircra = index_to_grade(self.min_index)
        # Pour le max, on prend la borne inf du grade SUIVANT - epsilon
        # afin d'inclure tous les blocs du grade max sélectionné
        if self.max_index < len(FONT_GRADES) - 1:
            _, next_ircra = index_to_grade(self.max_index + 1)
            max_ircra = next_ircra - 0.01
        else:
            # Dernier grade (8A) : on prend une valeur haute
            max_ircra = 30.0
        self.range_changed.emit(min_ircra, max_ircra)

    def get_range(self) -> tuple[float, float]:
        """Retourne la plage actuelle (min_ircra, max_ircra)."""
        _, min_ircra = index_to_grade(self.min_index)
        if self.max_index < len(FONT_GRADES) - 1:
            _, next_ircra = index_to_grade(self.max_index + 1)
            max_ircra = next_ircra - 0.01
        else:
            max_ircra = 30.0
        return min_ircra, max_ircra

    def get_range_grades(self) -> tuple[str, str]:
        """Retourne la plage actuelle en grades Font."""
        min_grade, _ = index_to_grade(self.min_index)
        max_grade, _ = index_to_grade(self.max_index)
        return min_grade, max_grade

    def set_range(self, min_ircra: float, max_ircra: float):
        """Définit la plage par valeurs IRCRA."""
        self.min_slider.setValue(ircra_to_index(min_ircra))
        self.max_slider.setValue(ircra_to_index(max_ircra))

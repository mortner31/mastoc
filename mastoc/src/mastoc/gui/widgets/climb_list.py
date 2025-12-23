"""
Widget de liste des climbs avec filtres.
"""

import logging
from pathlib import Path
from io import BytesIO

from PIL import Image as PILImage
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QListWidget, QListWidgetItem, QLineEdit, QComboBox,
    QLabel, QPushButton, QCheckBox, QGroupBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap

from mastoc.api.models import Climb, Hold
from mastoc.core.filters import ClimbFilter, ClimbFilterService
from mastoc.core.picto_cache import PictoCache
from mastoc.db import Database

logger = logging.getLogger(__name__)

# Taille des pictos dans la liste
PICTO_SIZE = 48


def pil_to_qicon(pil_image: PILImage.Image) -> QIcon:
    """Convertit une image PIL en QIcon."""
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)

    pixmap = QPixmap()
    pixmap.loadFromData(buffer.read())
    return QIcon(pixmap)


# Grades Fontainebleau avec valeurs IRCRA (valeurs réelles de la DB)
# Import depuis level_slider pour garder une seule source de vérité
from mastoc.gui.widgets.level_slider import FONT_GRADES


class ClimbListItem(QListWidgetItem):
    """Item de la liste représentant un climb."""

    def __init__(self, climb: Climb, icon: QIcon = None):
        self.climb = climb
        grade = climb.grade.font if climb.grade else "?"
        setter = climb.setter.full_name if climb.setter else "Inconnu"

        text = f"{climb.name}\n{grade} | {setter} | {climb.climbed_by} ascensions"
        super().__init__(text)

        self.setData(Qt.ItemDataRole.UserRole, climb.id)

        if icon:
            self.setIcon(icon)


class ClimbFilterWidget(QWidget):
    """Widget des filtres pour les climbs."""

    filters_changed = pyqtSignal(ClimbFilter)

    def __init__(self, filter_service: ClimbFilterService, parent=None):
        super().__init__(parent)
        self.filter_service = filter_service
        self.setup_ui()
        self.load_options()

    def setup_ui(self):
        """Configure l'interface des filtres."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Recherche texte
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un climb...")
        self.search_input.textChanged.connect(self.on_filter_changed)
        search_layout.addWidget(self.search_input)

        self.clear_btn = QPushButton("X")
        self.clear_btn.setMaximumWidth(30)
        self.clear_btn.clicked.connect(self.clear_filters)
        search_layout.addWidget(self.clear_btn)

        layout.addLayout(search_layout)

        # Filtres dans un groupe
        filters_group = QGroupBox("Filtres")
        filters_layout = QGridLayout(filters_group)

        # Grade min
        filters_layout.addWidget(QLabel("Grade min:"), 0, 0)
        self.grade_min_slider = QSlider(Qt.Orientation.Horizontal)
        self.grade_min_slider.setRange(0, len(FONT_GRADES) - 1)
        self.grade_min_slider.setValue(0)
        self.grade_min_slider.valueChanged.connect(self.on_grade_min_changed)
        filters_layout.addWidget(self.grade_min_slider, 0, 1)
        self.grade_min_label = QLabel(FONT_GRADES[0][0])
        self.grade_min_label.setMinimumWidth(35)
        filters_layout.addWidget(self.grade_min_label, 0, 2)

        # Grade max
        filters_layout.addWidget(QLabel("Grade max:"), 1, 0)
        self.grade_max_slider = QSlider(Qt.Orientation.Horizontal)
        self.grade_max_slider.setRange(0, len(FONT_GRADES) - 1)
        self.grade_max_slider.setValue(len(FONT_GRADES) - 1)
        self.grade_max_slider.valueChanged.connect(self.on_grade_max_changed)
        filters_layout.addWidget(self.grade_max_slider, 1, 1)
        self.grade_max_label = QLabel(FONT_GRADES[-1][0])
        self.grade_max_label.setMinimumWidth(35)
        filters_layout.addWidget(self.grade_max_label, 1, 2)

        # Affichage plage
        self.grade_range_label = QLabel(f"{FONT_GRADES[0][0]} - {FONT_GRADES[-1][0]}")
        self.grade_range_label.setStyleSheet("color: #666; font-style: italic;")
        filters_layout.addWidget(self.grade_range_label, 2, 0, 1, 3)

        # Setter
        filters_layout.addWidget(QLabel("Setter:"), 3, 0)
        self.setter_combo = QComboBox()
        self.setter_combo.addItem("Tous", None)
        self.setter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(self.setter_combo, 3, 1, 1, 2)

        # Feet rule
        filters_layout.addWidget(QLabel("Pieds:"), 4, 0)
        self.feet_combo = QComboBox()
        self.feet_combo.addItem("Tous", None)
        self.feet_combo.currentIndexChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(self.feet_combo, 4, 1, 1, 2)

        # Options
        self.benchmark_check = QCheckBox("Benchmarks seulement")
        self.benchmark_check.stateChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(self.benchmark_check, 5, 0, 1, 3)

        layout.addWidget(filters_group)

        # Tri
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Tri:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Date (récent)", "date_created")
        self.sort_combo.addItem("Grade", "grade")
        self.sort_combo.addItem("Nom", "name")
        self.sort_combo.addItem("Popularité", "climbed_by")
        self.sort_combo.addItem("Likes", "likes")
        self.sort_combo.currentIndexChanged.connect(self.on_filter_changed)
        sort_layout.addWidget(self.sort_combo)

        self.sort_desc_check = QCheckBox("Desc")
        self.sort_desc_check.setChecked(True)
        self.sort_desc_check.stateChanged.connect(self.on_filter_changed)
        sort_layout.addWidget(self.sort_desc_check)

        layout.addLayout(sort_layout)

    def load_options(self):
        """Charge les options depuis la base de données."""
        # Setters
        setters = self.filter_service.get_available_setters()
        for setter_id, name in setters:
            self.setter_combo.addItem(name, setter_id)

        # Feet rules
        feet_rules = self.filter_service.get_available_feet_rules()
        for rule in feet_rules:
            self.feet_combo.addItem(rule, rule)

    def on_grade_min_changed(self, value: int):
        """Appelé quand le slider grade min change."""
        max_val = self.grade_max_slider.value()
        if value > max_val:
            self.grade_min_slider.setValue(max_val)
            return
        grade_font, _ = FONT_GRADES[value]
        self.grade_min_label.setText(grade_font)
        self._update_grade_range_label()
        self.on_filter_changed()

    def on_grade_max_changed(self, value: int):
        """Appelé quand le slider grade max change."""
        min_val = self.grade_min_slider.value()
        if value < min_val:
            self.grade_max_slider.setValue(min_val)
            return
        grade_font, _ = FONT_GRADES[value]
        self.grade_max_label.setText(grade_font)
        self._update_grade_range_label()
        self.on_filter_changed()

    def _update_grade_range_label(self):
        """Met à jour l'affichage de la plage de grades."""
        min_idx = self.grade_min_slider.value()
        max_idx = self.grade_max_slider.value()
        min_grade = FONT_GRADES[min_idx][0]
        max_grade = FONT_GRADES[max_idx][0]
        self.grade_range_label.setText(f"{min_grade} - {max_grade}")

    def get_current_filter(self) -> ClimbFilter:
        """Retourne le filtre actuel."""
        filter_obj = ClimbFilter()

        # Recherche
        search = self.search_input.text().strip()
        if search:
            filter_obj.search_text = search

        # Grade min/max (IRCRA)
        min_idx = self.grade_min_slider.value()
        max_idx = self.grade_max_slider.value()
        _, min_ircra = FONT_GRADES[min_idx]
        # Pour le max, on prend la borne inf du grade SUIVANT - epsilon
        # afin d'inclure tous les blocs du grade max sélectionné
        if max_idx < len(FONT_GRADES) - 1:
            _, next_ircra = FONT_GRADES[max_idx + 1]
            max_ircra = next_ircra - 0.01
        else:
            max_ircra = 30.0
        filter_obj.grade_min = min_ircra
        filter_obj.grade_max = max_ircra

        logger.debug(f"Filtre grade: {FONT_GRADES[min_idx][0]} - {FONT_GRADES[max_idx][0]} (IRCRA {min_ircra}-{max_ircra})")

        # Setter
        setter_id = self.setter_combo.currentData()
        if setter_id:
            filter_obj.setter_ids = [setter_id]

        # Feet rule
        feet_rule = self.feet_combo.currentData()
        if feet_rule:
            filter_obj.feet_rules = [feet_rule]

        # Benchmark
        if self.benchmark_check.isChecked():
            filter_obj.is_benchmark = True

        # Tri
        filter_obj.sort_by = self.sort_combo.currentData()
        filter_obj.sort_desc = self.sort_desc_check.isChecked()

        return filter_obj

    def on_filter_changed(self):
        """Appelé quand un filtre change."""
        self.filters_changed.emit(self.get_current_filter())

    def clear_filters(self):
        """Réinitialise tous les filtres."""
        self.search_input.clear()
        self.grade_min_slider.setValue(0)
        self.grade_max_slider.setValue(len(FONT_GRADES) - 1)
        self.setter_combo.setCurrentIndex(0)
        self.feet_combo.setCurrentIndex(0)
        self.benchmark_check.setChecked(False)
        self.sort_combo.setCurrentIndex(0)
        self.sort_desc_check.setChecked(True)


class ClimbListWidget(QWidget):
    """Widget complet avec filtres et liste de climbs."""

    climb_selected = pyqtSignal(Climb)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.filter_service = ClimbFilterService(db)
        self.climbs: list[Climb] = []

        # Cache des pictos (persistant sur disque)
        self.picto_cache = PictoCache(size=PICTO_SIZE)
        self.icon_cache: dict[str, QIcon] = {}  # Cache mémoire des QIcon

        self.setup_ui()
        self.load_climbs()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Filtres
        self.filter_widget = ClimbFilterWidget(self.filter_service)
        self.filter_widget.filters_changed.connect(self.apply_filters)
        layout.addWidget(self.filter_widget)

        # Compteur
        self.count_label = QLabel("0 climbs")
        self.count_label.setStyleSheet("color: gray;")
        layout.addWidget(self.count_label)

        # Liste
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(PICTO_SIZE, PICTO_SIZE))
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.currentItemChanged.connect(self.on_current_item_changed)
        layout.addWidget(self.list_widget)

    def get_picto_cache(self) -> PictoCache:
        """Retourne le cache des pictos."""
        return self.picto_cache

    def load_climbs(self, filter_criteria: ClimbFilter = None):
        """Charge les climbs depuis la base de données."""
        if filter_criteria is None:
            filter_criteria = ClimbFilter()

        self.climbs = self.filter_service.filter_climbs(filter_criteria)
        self.update_list()

    def apply_filters(self, filter_criteria: ClimbFilter):
        """Applique les filtres et recharge la liste."""
        self.load_climbs(filter_criteria)

    def _get_picto_icon(self, climb: Climb) -> QIcon:
        """Récupère le picto d'un climb depuis le cache."""
        # Cache mémoire d'abord
        if climb.id in self.icon_cache:
            return self.icon_cache[climb.id]

        # Essayer le cache disque
        picto = self.picto_cache.get_picto(climb.id)
        if picto:
            icon = pil_to_qicon(picto)
            self.icon_cache[climb.id] = icon
            return icon

        # Pas de picto disponible
        return None

    def update_list(self):
        """Met à jour l'affichage de la liste."""
        self.list_widget.clear()

        for climb in self.climbs:
            icon = self._get_picto_icon(climb)
            item = ClimbListItem(climb, icon)
            self.list_widget.addItem(item)

        self.count_label.setText(f"{len(self.climbs)} climb{'s' if len(self.climbs) != 1 else ''}")

    def on_item_clicked(self, item: ClimbListItem):
        """Appelé lors d'un clic sur un item."""
        if hasattr(item, 'climb'):
            logger.debug(f"Clic sur climb: {item.climb.name}")
            self.climb_selected.emit(item.climb)

    def on_item_double_clicked(self, item: ClimbListItem):
        """Appelé lors d'un double-clic sur un item."""
        if hasattr(item, 'climb'):
            logger.debug(f"Double-clic sur climb: {item.climb.name}")
            self.climb_selected.emit(item.climb)

    def on_current_item_changed(self, current: ClimbListItem, previous: ClimbListItem):
        """Appelé lors de la navigation au clavier (flèches haut/bas)."""
        if current and hasattr(current, 'climb'):
            logger.debug(f"Navigation vers climb: {current.climb.name}")
            self.climb_selected.emit(current.climb)

    def get_selected_climb(self) -> Climb:
        """Retourne le climb sélectionné."""
        item = self.list_widget.currentItem()
        if item and hasattr(item, 'climb'):
            return item.climb
        return None

    def refresh(self):
        """Rafraîchit la liste avec les filtres actuels."""
        self.load_climbs(self.filter_widget.get_current_filter())

    def clear_icon_cache(self):
        """Vide le cache mémoire des icônes (pour recharger depuis le disque)."""
        self.icon_cache.clear()

"""
Panel affichant les listes personnalisées de l'utilisateur.
"""

from typing import Optional
from threading import Thread

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTabWidget, QPushButton, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from mastoc.api.client import StoktAPI
from mastoc.api.models import ClimbList, ListItem, Climb


class MyListsPanel(QWidget):
    """
    Panel affichant les listes personnalisées.

    Onglets :
    - Mes listes (listes personnelles)
    - Populaires (listes du gym)
    """

    climb_selected = pyqtSignal(Climb)
    list_selected = pyqtSignal(ClimbList)

    def __init__(self, api: StoktAPI, gym_id: str, user_id: str, parent=None):
        super().__init__(parent)
        self.api = api
        self.gym_id = gym_id
        self.user_id = user_id

        # Donnees
        self.my_lists: list[ClimbList] = []
        self.gym_lists: list[ClimbList] = []
        self.current_list: Optional[ClimbList] = None
        self.current_items: list[ListItem] = []

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Splitter vertical : listes en haut, items en bas
        splitter = QSplitter(Qt.Orientation.Vertical)

        # === Partie haute : selection de liste ===
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(8, 8, 8, 4)

        # Titre
        title = QLabel("Listes")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_layout.addWidget(title)

        # Tabs pour les types de listes
        self.tabs = QTabWidget()

        # Tab Mes listes
        self.my_lists_widget = QWidget()
        my_layout = QVBoxLayout(self.my_lists_widget)
        my_layout.setContentsMargins(0, 0, 0, 0)
        self.my_lists_view = QListWidget()
        self.my_lists_view.itemClicked.connect(self._on_my_list_clicked)
        my_layout.addWidget(self.my_lists_view)
        self.tabs.addTab(self.my_lists_widget, "Mes listes")

        # Tab Populaires
        self.gym_lists_widget = QWidget()
        gym_layout = QVBoxLayout(self.gym_lists_widget)
        gym_layout.setContentsMargins(0, 0, 0, 0)
        self.gym_lists_view = QListWidget()
        self.gym_lists_view.itemClicked.connect(self._on_gym_list_clicked)
        gym_layout.addWidget(self.gym_lists_view)
        self.tabs.addTab(self.gym_lists_widget, "Populaires")

        top_layout.addWidget(self.tabs)

        # Bouton refresh
        refresh_btn = QPushButton("Rafraichir")
        refresh_btn.clicked.connect(self.refresh)
        top_layout.addWidget(refresh_btn)

        splitter.addWidget(top_widget)

        # === Partie basse : items de la liste selectionnee ===
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(8, 4, 8, 8)

        # Header liste selectionnee
        self.list_header = QLabel("Selectionnez une liste")
        self.list_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #666;")
        bottom_layout.addWidget(self.list_header)

        # Liste des items (climbs)
        self.items_view = QListWidget()
        self.items_view.itemDoubleClicked.connect(self._on_item_double_clicked)
        bottom_layout.addWidget(self.items_view)

        splitter.addWidget(bottom_widget)

        # Proportions initiales
        splitter.setSizes([200, 300])

        layout.addWidget(splitter)

        # Loading indicator
        self.loading_label = QLabel("Chargement...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: gray;")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

    def refresh(self):
        """Recharge toutes les donnees."""
        self.loading_label.show()
        Thread(target=self._load_lists, daemon=True).start()

    def _load_lists(self):
        """Charge les listes (thread)."""
        # Ces méthodes n'existent que sur StoktAPI (pas Railway)
        if hasattr(self.api, 'get_user_lists'):
            try:
                self.my_lists = self.api.get_user_lists(self.user_id)
            except Exception as e:
                print(f"Erreur chargement mes listes: {e}")
                self.my_lists = []
        else:
            self.my_lists = []

        if hasattr(self.api, 'get_gym_lists'):
            try:
                self.gym_lists = self.api.get_gym_lists(self.gym_id, page_size=50)
            except Exception as e:
                print(f"Erreur chargement listes gym: {e}")
                self.gym_lists = []
        else:
            self.gym_lists = []

        # Mise a jour UI dans le thread principal
        from PyQt6.QtCore import QMetaObject, Q_ARG, Qt as QtCore_Qt
        QMetaObject.invokeMethod(self, "_update_lists_ui", QtCore_Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def _update_lists_ui(self):
        """Met a jour l'interface des listes."""
        self.loading_label.hide()

        # Mes listes
        self.my_lists_view.clear()
        self.tabs.setTabText(0, f"Mes listes ({len(self.my_lists)})")
        for lst in self.my_lists:
            item = QListWidgetItem(f"{lst.name} ({lst.climbs_count} climbs)")
            item.setData(Qt.ItemDataRole.UserRole, lst)
            self.my_lists_view.addItem(item)

        # Listes populaires
        self.gym_lists_view.clear()
        self.tabs.setTabText(1, f"Populaires ({len(self.gym_lists)})")
        for lst in self.gym_lists:
            owner = f" - {lst.owner_name}" if lst.owner_name else ""
            item = QListWidgetItem(f"{lst.name} ({lst.climbs_count}){owner}")
            item.setData(Qt.ItemDataRole.UserRole, lst)
            self.gym_lists_view.addItem(item)

    def _on_my_list_clicked(self, item: QListWidgetItem):
        """Liste personnelle selectionnee."""
        lst = item.data(Qt.ItemDataRole.UserRole)
        if lst:
            self._load_list_items(lst)

    def _on_gym_list_clicked(self, item: QListWidgetItem):
        """Liste gym selectionnee."""
        lst = item.data(Qt.ItemDataRole.UserRole)
        if lst:
            self._load_list_items(lst)

    def _load_list_items(self, lst: ClimbList):
        """Charge les items d'une liste."""
        self.current_list = lst
        self.list_header.setText(f"{lst.name} - Chargement...")
        self.list_selected.emit(lst)
        Thread(target=self._fetch_items, args=(lst.id,), daemon=True).start()

    def _fetch_items(self, list_id: str):
        """Recupere les items (thread)."""
        try:
            self.current_items = self.api.get_list_items(list_id)
        except Exception as e:
            print(f"Erreur chargement items: {e}")
            self.current_items = []

        from PyQt6.QtCore import QMetaObject, Qt as QtCore_Qt
        QMetaObject.invokeMethod(self, "_update_items_ui", QtCore_Qt.ConnectionType.QueuedConnection)

    def _update_items_ui(self):
        """Met a jour l'interface des items."""
        self.items_view.clear()

        if not self.current_list:
            self.list_header.setText("Selectionnez une liste")
            return

        self.list_header.setText(f"{self.current_list.name} ({len(self.current_items)} climbs)")

        for list_item in self.current_items:
            climb = list_item.climb
            grade = climb.grade.font if climb.grade else "?"
            setter = climb.setter.full_name if climb.setter else ""
            text = f"{climb.name} ({grade})"
            if setter:
                text += f" - {setter}"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, climb)
            self.items_view.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Climb selectionne dans la liste."""
        climb = item.data(Qt.ItemDataRole.UserRole)
        if climb:
            self.climb_selected.emit(climb)

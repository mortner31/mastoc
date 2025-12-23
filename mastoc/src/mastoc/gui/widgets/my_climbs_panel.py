"""
Panel affichant les climbs de l'utilisateur (favoris, likes, ascensions).
"""

from typing import Optional, Callable
from threading import Thread

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTabWidget, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from mastoc.api.client import StoktAPI
from mastoc.api.models import Climb


class MyClimbsPanel(QWidget):
    """
    Panel affichant les climbs de l'utilisateur.

    Onglets :
    - Favoris (bookmarks)
    - Likes
    - Ascensions (sends)
    """

    climb_selected = pyqtSignal(Climb)

    def __init__(self, api: StoktAPI, gym_id: str, parent=None):
        super().__init__(parent)
        self.api = api
        self.gym_id = gym_id

        # Données
        self.bookmarked_climbs: list[Climb] = []
        self.liked_climbs: list[Climb] = []
        self.sent_climbs: list[Climb] = []

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Mes Climbs")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()

        # Tab Favoris
        self.bookmarks_widget = QWidget()
        bookmarks_layout = QVBoxLayout(self.bookmarks_widget)
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self._on_bookmark_selected)
        bookmarks_layout.addWidget(self.bookmarks_list)
        self.tabs.addTab(self.bookmarks_widget, "⭐ Favoris")

        # Tab Likes
        self.likes_widget = QWidget()
        likes_layout = QVBoxLayout(self.likes_widget)
        self.likes_list = QListWidget()
        self.likes_list.itemDoubleClicked.connect(self._on_like_selected)
        likes_layout.addWidget(self.likes_list)
        self.tabs.addTab(self.likes_widget, "❤ Likes")

        # Tab Ascensions
        self.sends_widget = QWidget()
        sends_layout = QVBoxLayout(self.sends_widget)
        self.sends_list = QListWidget()
        self.sends_list.itemDoubleClicked.connect(self._on_send_selected)
        sends_layout.addWidget(self.sends_list)
        self.tabs.addTab(self.sends_widget, "👤 Ascensions")

        layout.addWidget(self.tabs)

        # Bouton refresh
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)

        # Loading
        self.loading_label = QLabel("Chargement...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: gray;")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

    def refresh(self):
        """Recharge toutes les données."""
        self.loading_label.show()
        Thread(target=self._load_all, daemon=True).start()

    def _load_all(self):
        """Charge toutes les données (thread)."""
        try:
            self.bookmarked_climbs = self.api.get_my_bookmarked_climbs(self.gym_id)
        except Exception:
            self.bookmarked_climbs = []

        try:
            self.liked_climbs = self.api.get_my_liked_climbs(self.gym_id)
        except Exception:
            self.liked_climbs = []

        try:
            self.sent_climbs = self.api.get_my_sent_climbs(self.gym_id)
        except Exception:
            self.sent_climbs = []

        # Mettre à jour l'UI (doit être fait dans le thread principal)
        # On utilise QMetaObject.invokeMethod ou on appelle directement
        self._update_ui()

    def _update_ui(self):
        """Met à jour l'interface avec les données."""
        self.loading_label.hide()

        # Favoris
        self.bookmarks_list.clear()
        self.tabs.setTabText(0, f"⭐ Favoris ({len(self.bookmarked_climbs)})")
        for climb in self.bookmarked_climbs:
            grade = climb.grade.font if climb.grade else "?"
            item = QListWidgetItem(f"{climb.name} ({grade})")
            item.setData(Qt.ItemDataRole.UserRole, climb)
            self.bookmarks_list.addItem(item)

        # Likes
        self.likes_list.clear()
        self.tabs.setTabText(1, f"❤ Likes ({len(self.liked_climbs)})")
        for climb in self.liked_climbs:
            grade = climb.grade.font if climb.grade else "?"
            item = QListWidgetItem(f"{climb.name} ({grade})")
            item.setData(Qt.ItemDataRole.UserRole, climb)
            self.likes_list.addItem(item)

        # Ascensions
        self.sends_list.clear()
        self.tabs.setTabText(2, f"👤 Ascensions ({len(self.sent_climbs)})")
        for climb in self.sent_climbs:
            grade = climb.grade.font if climb.grade else "?"
            item = QListWidgetItem(f"{climb.name} ({grade})")
            item.setData(Qt.ItemDataRole.UserRole, climb)
            self.sends_list.addItem(item)

    def _on_bookmark_selected(self, item: QListWidgetItem):
        climb = item.data(Qt.ItemDataRole.UserRole)
        if climb:
            self.climb_selected.emit(climb)

    def _on_like_selected(self, item: QListWidgetItem):
        climb = item.data(Qt.ItemDataRole.UserRole)
        if climb:
            self.climb_selected.emit(climb)

    def _on_send_selected(self, item: QListWidgetItem):
        climb = item.data(Qt.ItemDataRole.UserRole)
        if climb:
            self.climb_selected.emit(climb)

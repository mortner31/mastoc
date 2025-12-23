"""
Panel d'affichage des données sociales (ascensions, commentaires, likes).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTabWidget, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from mastoc.api.models import Effort, Comment, Like
from mastoc.core.social_loader import SocialData


class SocialPanel(QWidget):
    """
    Panel affichant les données sociales d'un climb.

    Contient des onglets pour :
    - Ascensions (sends)
    - Commentaires
    - Likes
    """

    like_clicked = pyqtSignal()
    bookmark_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabs
        self.tabs = QTabWidget()

        # Tab Ascensions
        self.sends_widget = QWidget()
        sends_layout = QVBoxLayout(self.sends_widget)
        self.sends_list = QListWidget()
        self.sends_list.setAlternatingRowColors(True)
        sends_layout.addWidget(self.sends_list)
        self.tabs.addTab(self.sends_widget, "👤 Ascensions")

        # Tab Commentaires
        self.comments_widget = QWidget()
        comments_layout = QVBoxLayout(self.comments_widget)
        self.comments_list = QListWidget()
        self.comments_list.setAlternatingRowColors(True)
        self.comments_list.setWordWrap(True)
        comments_layout.addWidget(self.comments_list)
        self.tabs.addTab(self.comments_widget, "💬 Commentaires")

        # Tab Likes
        self.likes_widget = QWidget()
        likes_layout = QVBoxLayout(self.likes_widget)
        self.likes_list = QListWidget()
        self.likes_list.setAlternatingRowColors(True)
        likes_layout.addWidget(self.likes_list)
        self.tabs.addTab(self.likes_widget, "❤ Likes")

        layout.addWidget(self.tabs)

        # Boutons d'action
        actions_layout = QHBoxLayout()

        self.like_btn = QPushButton("❤ Like")
        self.like_btn.clicked.connect(self.like_clicked.emit)
        actions_layout.addWidget(self.like_btn)

        self.bookmark_btn = QPushButton("⭐ Favori")
        self.bookmark_btn.clicked.connect(self.bookmark_clicked.emit)
        actions_layout.addWidget(self.bookmark_btn)

        layout.addLayout(actions_layout)

        # État loading
        self.loading_label = QLabel("Chargement...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: gray; font-style: italic;")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

    def set_loading(self, loading: bool):
        """Affiche/masque l'indicateur de chargement."""
        if loading:
            self.loading_label.show()
            self.tabs.hide()
        else:
            self.loading_label.hide()
            self.tabs.show()

    def set_data(self, data: SocialData):
        """Affiche les données sociales."""
        self.set_loading(False)

        # Ascensions
        self.sends_list.clear()
        self.tabs.setTabText(0, f"👤 Ascensions ({len(data.sends)})")
        for send in data.sends:
            flash = " ⚡" if send.is_flash else ""
            date = send.date[:10] if send.date else ""
            item = QListWidgetItem(f"{send.user.full_name}{flash} - {date}")
            self.sends_list.addItem(item)

        if not data.sends:
            item = QListWidgetItem("Aucune ascension")
            item.setForeground(Qt.GlobalColor.gray)
            self.sends_list.addItem(item)

        # Commentaires
        self.comments_list.clear()
        self.tabs.setTabText(1, f"💬 Commentaires ({len(data.comments)})")
        for comment in data.comments:
            date = comment.date[:10] if comment.date else ""
            item = QListWidgetItem(f"{comment.user.full_name} ({date}):\n{comment.text}")
            self.comments_list.addItem(item)

        if not data.comments:
            item = QListWidgetItem("Aucun commentaire")
            item.setForeground(Qt.GlobalColor.gray)
            self.comments_list.addItem(item)

        # Likes
        self.likes_list.clear()
        self.tabs.setTabText(2, f"❤ Likes ({len(data.likes)})")
        for like in data.likes:
            item = QListWidgetItem(like.user.full_name)
            self.likes_list.addItem(item)

        if not data.likes:
            item = QListWidgetItem("Aucun like")
            item.setForeground(Qt.GlobalColor.gray)
            self.likes_list.addItem(item)

    def set_user_status(self, liked: bool, bookmarked: bool):
        """Met à jour l'état des boutons selon le statut utilisateur."""
        if liked:
            self.like_btn.setText("❤ Unlike")
            self.like_btn.setStyleSheet("background-color: #ffcccc;")
        else:
            self.like_btn.setText("❤ Like")
            self.like_btn.setStyleSheet("")

        if bookmarked:
            self.bookmark_btn.setText("⭐ Retirer")
            self.bookmark_btn.setStyleSheet("background-color: #ffffcc;")
        else:
            self.bookmark_btn.setText("⭐ Favori")
            self.bookmark_btn.setStyleSheet("")

    def clear(self):
        """Vide toutes les listes."""
        self.sends_list.clear()
        self.comments_list.clear()
        self.likes_list.clear()
        self.tabs.setTabText(0, "👤 Ascensions")
        self.tabs.setTabText(1, "💬 Commentaires")
        self.tabs.setTabText(2, "❤ Likes")


class SocialPanelCompact(QWidget):
    """
    Version compacte du panel social (juste les compteurs + boutons).

    Pour intégration dans des espaces réduits.
    """

    like_clicked = pyqtSignal()
    bookmark_clicked = pyqtSignal()
    expand_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Compteurs
        self.sends_label = QLabel("👤 0")
        self.sends_label.setToolTip("Ascensions")
        layout.addWidget(self.sends_label)

        self.comments_label = QLabel("💬 0")
        self.comments_label.setToolTip("Commentaires")
        layout.addWidget(self.comments_label)

        self.likes_label = QLabel("❤ 0")
        self.likes_label.setToolTip("Likes")
        layout.addWidget(self.likes_label)

        layout.addStretch()

        # Boutons
        self.like_btn = QPushButton("❤")
        self.like_btn.setMaximumWidth(40)
        self.like_btn.clicked.connect(self.like_clicked.emit)
        layout.addWidget(self.like_btn)

        self.bookmark_btn = QPushButton("⭐")
        self.bookmark_btn.setMaximumWidth(40)
        self.bookmark_btn.clicked.connect(self.bookmark_clicked.emit)
        layout.addWidget(self.bookmark_btn)

        self.expand_btn = QPushButton("▼")
        self.expand_btn.setMaximumWidth(40)
        self.expand_btn.setToolTip("Voir détails")
        self.expand_btn.clicked.connect(self.expand_clicked.emit)
        layout.addWidget(self.expand_btn)

    def set_counts(self, sends: int, comments: int, likes: int):
        """Met à jour les compteurs."""
        self.sends_label.setText(f"👤 {sends}")
        self.comments_label.setText(f"💬 {comments}")
        self.likes_label.setText(f"❤ {likes}")

    def set_user_status(self, liked: bool, bookmarked: bool):
        """Met à jour l'état des boutons."""
        self.like_btn.setStyleSheet("background-color: #ffcccc;" if liked else "")
        self.bookmark_btn.setStyleSheet("background-color: #ffffcc;" if bookmarked else "")

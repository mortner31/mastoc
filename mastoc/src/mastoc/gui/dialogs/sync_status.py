"""
Dialog pour afficher l'état de synchronisation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QGroupBox,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from mastoc.core.sync_stats import get_sync_stats, get_local_climbs, SyncStats, LocalClimb


class LoadStatsThread(QThread):
    """Thread pour charger les stats en arrière-plan."""
    finished = pyqtSignal(object, list)  # (SyncStats, list[LocalClimb])
    error = pyqtSignal(str)

    def run(self):
        try:
            stats = get_sync_stats()
            local = get_local_climbs() if stats.local_climbs > 0 else []
            self.finished.emit(stats, local)
        except Exception as e:
            self.error.emit(str(e))


class SyncStatusDialog(QDialog):
    """Dialog affichant les statistiques de synchronisation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("État de Synchronisation")
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)

        self._setup_ui()
        self._load_stats()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Groupe Stats
        stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(stats_group)

        self.label_total = QLabel("Total climbs: ...")
        self.label_synced = QLabel("Synchronisés: ...")
        self.label_local = QLabel("Locaux: ...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% synchronisés")

        stats_layout.addWidget(self.label_total)
        stats_layout.addWidget(self.label_synced)
        stats_layout.addWidget(self.label_local)
        stats_layout.addWidget(self.progress_bar)

        layout.addWidget(stats_group)

        # Groupe Climbs Locaux
        local_group = QGroupBox("Climbs Locaux (non synchronisés)")
        local_layout = QVBoxLayout(local_group)

        self.local_list = QListWidget()
        self.local_list.setAlternatingRowColors(True)
        local_layout.addWidget(self.local_list)

        layout.addWidget(local_group)

        # Boutons
        buttons_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self._load_stats)

        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def _load_stats(self):
        """Lance le chargement des stats."""
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Chargement...")
        self.local_list.clear()
        self.local_list.addItem("Chargement...")

        self._thread = LoadStatsThread()
        self._thread.finished.connect(self._on_stats_loaded)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_stats_loaded(self, stats: SyncStats, local_climbs: list[LocalClimb]):
        """Callback quand les stats sont chargées."""
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Rafraîchir")

        self.label_total.setText(f"Total climbs: {stats.total_climbs}")
        self.label_synced.setText(f"Synchronisés: {stats.synced_climbs}")
        self.label_local.setText(f"Locaux: {stats.local_climbs}")

        self.progress_bar.setValue(int(stats.sync_percentage))

        self.local_list.clear()
        if not local_climbs:
            self.local_list.addItem("Aucun climb local")
        else:
            for c in local_climbs:
                grade = c.grade or "?"
                setter = c.setter_name or "inconnu"
                item = QListWidgetItem(f"{c.name} ({grade}) - {setter}")
                self.local_list.addItem(item)

    def _on_error(self, error_msg: str):
        """Callback en cas d'erreur."""
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Rafraîchir")
        self.local_list.clear()

        QMessageBox.warning(self, "Erreur", f"Impossible de charger les stats:\n{error_msg}")

"""
Dialog de synchronisation avec choix du mode (incrémental/complet).
"""

from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox, QProgressBar,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class SyncWorker(QThread):
    """Worker thread pour la synchronisation."""

    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(object)  # SyncResult
    error = pyqtSignal(str)

    def __init__(self, sync_manager, mode: str, parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.mode = mode

    def run(self):
        try:
            if self.mode == "incremental":
                result = self.sync_manager.sync_incremental(
                    callback=lambda c, t, m: self.progress.emit(c, t, m)
                )
            else:
                result = self.sync_manager.sync_full(
                    callback=lambda c, t, m: self.progress.emit(c, t, m)
                )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SyncDialog(QDialog):
    """
    Dialog de synchronisation avec choix du mode.

    Affiche les statistiques de sync et permet de choisir entre
    sync incrémentale (rapide) et sync complète (tout télécharger).
    """

    def __init__(self, sync_manager, db, parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.db = db
        self.worker = None
        self.result = None

        self.setWindowTitle("Synchronisation")
        self.setMinimumWidth(450)
        self.setModal(True)

        self.setup_ui()
        self.update_status()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Section status actuel
        status_group = QGroupBox("Status actuel")
        status_layout = QVBoxLayout(status_group)

        self.last_sync_label = QLabel("Dernière sync: -")
        self.climb_count_label = QLabel("Climbs en base: -")
        self.hold_count_label = QLabel("Prises en base: -")

        status_layout.addWidget(self.last_sync_label)
        status_layout.addWidget(self.climb_count_label)
        status_layout.addWidget(self.hold_count_label)
        layout.addWidget(status_group)

        # Section choix du mode
        mode_group = QGroupBox("Mode de synchronisation")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_group = QButtonGroup(self)

        # Mode incrémental (recommandé)
        self.incremental_radio = QRadioButton("Incrémentale (recommandé)")
        self.incremental_radio.setChecked(True)
        self.incremental_desc = QLabel(
            "Télécharge uniquement les nouveaux climbs depuis la dernière sync.\n"
            "Rapide et économe en bande passante."
        )
        self.incremental_desc.setStyleSheet("color: gray; margin-left: 20px;")
        self.incremental_desc.setWordWrap(True)

        # Mode complet
        self.full_radio = QRadioButton("Complète")
        self.full_desc = QLabel(
            "Télécharge tous les climbs depuis l'API.\n"
            "Utiliser si des données semblent manquantes."
        )
        self.full_desc.setStyleSheet("color: gray; margin-left: 20px;")
        self.full_desc.setWordWrap(True)

        self.mode_group.addButton(self.incremental_radio, 0)
        self.mode_group.addButton(self.full_radio, 1)

        mode_layout.addWidget(self.incremental_radio)
        mode_layout.addWidget(self.incremental_desc)
        mode_layout.addWidget(self.full_radio)
        mode_layout.addWidget(self.full_desc)

        layout.addWidget(mode_group)

        # Barre de progression (cachée au départ)
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_label = QLabel("En attente...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        self.progress_frame.hide()

        layout.addWidget(self.progress_frame)

        # Résultats (cachés au départ)
        self.result_frame = QFrame()
        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(0, 0, 0, 0)

        self.result_title = QLabel()
        self.result_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.result_details = QLabel()
        self.result_details.setWordWrap(True)

        result_layout.addWidget(self.result_title)
        result_layout.addWidget(self.result_details)
        self.result_frame.hide()

        layout.addWidget(self.result_frame)

        # Boutons
        button_layout = QHBoxLayout()

        self.sync_button = QPushButton("Synchroniser")
        self.sync_button.clicked.connect(self.start_sync)
        self.sync_button.setDefault(True)

        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.sync_button)

        layout.addLayout(button_layout)

    def update_status(self):
        """Met à jour les labels de status."""
        status = self.sync_manager.get_sync_status()

        last_sync = status.get("last_sync")
        if last_sync:
            # Formater la date
            dt = datetime.fromisoformat(last_sync)
            self.last_sync_label.setText(
                f"Dernière sync: {dt.strftime('%d/%m/%Y %H:%M')}"
            )
            # Activer le mode incrémental si déjà synchronisé
            self.incremental_radio.setEnabled(True)
        else:
            self.last_sync_label.setText("Dernière sync: jamais")
            # Forcer sync complète si première fois
            self.full_radio.setChecked(True)
            self.incremental_radio.setEnabled(False)

        self.climb_count_label.setText(
            f"Climbs en base: {status.get('climb_count', 0)}"
        )
        self.hold_count_label.setText(
            f"Prises en base: {status.get('hold_count', 0)}"
        )

    def start_sync(self):
        """Démarre la synchronisation."""
        mode = "incremental" if self.incremental_radio.isChecked() else "full"

        # Afficher la progression
        self.progress_frame.show()
        self.result_frame.hide()
        self.sync_button.setEnabled(False)
        self.incremental_radio.setEnabled(False)
        self.full_radio.setEnabled(False)

        # Démarrer le worker
        self.worker = SyncWorker(self.sync_manager, mode, self)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current: int, total: int, message: str):
        """Appelé lors de la progression."""
        if total > 0:
            self.progress_bar.setValue(int(current / total * 100))
        self.progress_label.setText(message)

    def on_finished(self, result):
        """Appelé quand la sync est terminée."""
        self.result = result
        self.progress_frame.hide()
        self.result_frame.show()

        if result.success:
            self.result_title.setText("Synchronisation réussie")
            self.result_title.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: green;"
            )

            # Construire le message de résultat
            mode_str = "Incrémentale" if result.mode == "incremental" else "Complète"
            details = [f"Mode: {mode_str}"]

            if result.climbs_downloaded > 0:
                details.append(f"Climbs téléchargés: {result.climbs_downloaded}")

            details.append(f"Climbs ajoutés: {result.climbs_added}")

            if result.climbs_updated > 0:
                details.append(f"Climbs mis à jour: {result.climbs_updated}")

            if result.holds_added > 0:
                details.append(f"Prises ajoutées: {result.holds_added}")

            details.append(f"Total en base: {result.total_climbs_local} climbs")

            self.result_details.setText("\n".join(details))

            # Mettre à jour les labels de status
            self.update_status()

            # Changer le bouton
            self.sync_button.setText("Fermer")
            self.sync_button.clicked.disconnect()
            self.sync_button.clicked.connect(self.accept)
            self.sync_button.setEnabled(True)
            self.cancel_button.hide()
        else:
            self.result_title.setText("Erreur de synchronisation")
            self.result_title.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: red;"
            )
            self.result_details.setText("\n".join(result.errors))

            # Réactiver les boutons
            self.sync_button.setEnabled(True)
            self.incremental_radio.setEnabled(True)
            self.full_radio.setEnabled(True)

    def on_error(self, error_msg: str):
        """Appelé en cas d'erreur."""
        self.progress_frame.hide()
        QMessageBox.critical(self, "Erreur", f"Erreur de synchronisation:\n{error_msg}")
        self.sync_button.setEnabled(True)
        self.incremental_radio.setEnabled(True)
        self.full_radio.setEnabled(True)

    def get_result(self):
        """Retourne le résultat de la synchronisation."""
        return self.result

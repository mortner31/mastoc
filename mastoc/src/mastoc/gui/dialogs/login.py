"""
Dialog d'authentification pour l'API Stokt.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from mastoc.api.client import StoktAPI, AuthenticationError


class LoginDialog(QDialog):
    """Dialog de connexion à l'API Stokt."""

    logged_in = pyqtSignal(str)  # Émet le token après connexion réussie

    def __init__(self, api: StoktAPI = None, parent=None):
        super().__init__(parent)
        self.api = api or StoktAPI()
        self.token = None

        self.setWindowTitle("Connexion Stokt")
        self.setMinimumWidth(350)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Connexion à Stokt")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Formulaire
        form = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email ou nom d'utilisateur")
        form.addRow("Utilisateur:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.login)
        form.addRow("Mot de passe:", self.password_input)

        layout.addLayout(form)

        # Message d'erreur
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; margin-top: 5px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # Boutons
        buttons = QHBoxLayout()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)

        self.login_btn = QPushButton("Connexion")
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self.login)
        buttons.addWidget(self.login_btn)

        layout.addLayout(buttons)

        # Hint pour token manuel
        hint = QLabel("Ou utilisez un token existant:")
        hint.setStyleSheet("color: gray; margin-top: 10px;")
        layout.addWidget(hint)

        token_layout = QHBoxLayout()
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Token d'authentification")
        token_layout.addWidget(self.token_input)

        self.token_btn = QPushButton("Utiliser")
        self.token_btn.clicked.connect(self.use_token)
        token_layout.addWidget(self.token_btn)

        layout.addLayout(token_layout)

    def login(self):
        """Tente de se connecter avec username/password."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Veuillez remplir tous les champs")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Connexion...")

        try:
            result = self.api.login(username, password)
            self.token = result.get("token")
            if self.token:
                self.logged_in.emit(self.token)
                self.accept()
            else:
                self.show_error("Token non reçu dans la réponse")
        except AuthenticationError as e:
            self.show_error(f"Erreur d'authentification: {e}")
        except Exception as e:
            self.show_error(f"Erreur de connexion: {e}")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Connexion")

    def use_token(self):
        """Utilise un token entré manuellement."""
        token = self.token_input.text().strip()

        if not token:
            self.show_error("Veuillez entrer un token")
            return

        self.api.set_token(token)

        # Vérifier le token en appelant l'API
        try:
            self.api.get_user_profile()
            self.token = token
            self.logged_in.emit(self.token)
            self.accept()
        except AuthenticationError:
            self.show_error("Token invalide ou expiré")
        except Exception as e:
            self.show_error(f"Erreur de vérification: {e}")

    def show_error(self, message: str):
        """Affiche un message d'erreur."""
        self.error_label.setText(message)
        self.error_label.show()

    def get_token(self) -> str:
        """Retourne le token après connexion réussie."""
        return self.token


class TokenExpiredDialog(QDialog):
    """Dialog affiché quand le token a expiré."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session expirée")
        self.setModal(True)

        layout = QVBoxLayout(self)

        message = QLabel(
            "Votre session a expiré.\n"
            "Veuillez vous reconnecter pour continuer."
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        buttons = QHBoxLayout()

        self.close_btn = QPushButton("Fermer")
        self.close_btn.clicked.connect(self.reject)
        buttons.addWidget(self.close_btn)

        self.reconnect_btn = QPushButton("Reconnecter")
        self.reconnect_btn.setDefault(True)
        self.reconnect_btn.clicked.connect(self.accept)
        buttons.addWidget(self.reconnect_btn)

        layout.addLayout(buttons)

    def show_login_dialog(self, api: StoktAPI) -> bool:
        """Affiche le dialog et ouvre la connexion si demandé."""
        if self.exec() == QDialog.DialogCode.Accepted:
            login = LoginDialog(api, self.parent())
            return login.exec() == QDialog.DialogCode.Accepted
        return False

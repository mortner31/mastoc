"""
Dialogs d'authentification mastoc.

- MastocLoginDialog : Connexion/Inscription
- ProfileDialog : Profil utilisateur
- PasswordResetDialog : Reset mot de passe
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QTabWidget, QWidget,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from mastoc.core.auth import AuthManager, AuthError, UserProfile


class MastocLoginDialog(QDialog):
    """
    Dialog de connexion/inscription mastoc.

    Deux onglets :
    - Connexion : email/username + password
    - Inscription : créer un nouveau compte
    """

    logged_in = pyqtSignal(object)  # Émet UserProfile après connexion réussie

    def __init__(self, auth_manager: AuthManager, parent=None):
        super().__init__(parent)
        self.auth = auth_manager

        self.setWindowTitle("Connexion mastoc")
        self.setMinimumWidth(400)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("mastoc")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #2196F3; margin: 10px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()

        # Tab Connexion
        login_tab = QWidget()
        self.setup_login_tab(login_tab)
        self.tabs.addTab(login_tab, "Connexion")

        # Tab Inscription
        register_tab = QWidget()
        self.setup_register_tab(register_tab)
        self.tabs.addTab(register_tab, "Inscription")

        layout.addWidget(self.tabs)

        # Message d'erreur global
        self.error_label = QLabel()
        self.error_label.setStyleSheet(
            "color: #f44336; margin: 5px; padding: 5px; "
            "background-color: #ffebee; border-radius: 4px;"
        )
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # Lien mot de passe oublié
        forgot_link = QLabel('<a href="#">Mot de passe oublié ?</a>')
        forgot_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forgot_link.setStyleSheet("margin-top: 10px;")
        forgot_link.linkActivated.connect(self.show_reset_dialog)
        layout.addWidget(forgot_link)

    def setup_login_tab(self, tab: QWidget):
        """Configure l'onglet connexion."""
        layout = QVBoxLayout(tab)

        form = QFormLayout()

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email ou nom d'utilisateur")
        form.addRow("Identifiant:", self.login_email)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Mot de passe")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.returnPressed.connect(self.do_login)
        form.addRow("Mot de passe:", self.login_password)

        layout.addLayout(form)

        # Boutons
        buttons = QHBoxLayout()

        self.cancel_login_btn = QPushButton("Annuler")
        self.cancel_login_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_login_btn)

        self.login_btn = QPushButton("Connexion")
        self.login_btn.setDefault(True)
        self.login_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; "
            "padding: 8px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.login_btn.clicked.connect(self.do_login)
        buttons.addWidget(self.login_btn)

        layout.addLayout(buttons)

    def setup_register_tab(self, tab: QWidget):
        """Configure l'onglet inscription."""
        layout = QVBoxLayout(tab)

        form = QFormLayout()

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("votre@email.com")
        form.addRow("Email:", self.reg_email)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("3-50 caractères")
        form.addRow("Nom d'utilisateur:", self.reg_username)

        self.reg_fullname = QLineEdit()
        self.reg_fullname.setPlaceholderText("Prénom Nom")
        form.addRow("Nom complet:", self.reg_fullname)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("8 caractères minimum")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Mot de passe:", self.reg_password)

        self.reg_password2 = QLineEdit()
        self.reg_password2.setPlaceholderText("Confirmez le mot de passe")
        self.reg_password2.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password2.returnPressed.connect(self.do_register)
        form.addRow("Confirmation:", self.reg_password2)

        layout.addLayout(form)

        # Boutons
        buttons = QHBoxLayout()

        self.cancel_reg_btn = QPushButton("Annuler")
        self.cancel_reg_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_reg_btn)

        self.register_btn = QPushButton("Créer le compte")
        self.register_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 8px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #388E3C; }"
        )
        self.register_btn.clicked.connect(self.do_register)
        buttons.addWidget(self.register_btn)

        layout.addLayout(buttons)

    def do_login(self):
        """Effectue la connexion."""
        email = self.login_email.text().strip()
        password = self.login_password.text()

        if not email or not password:
            self.show_error("Veuillez remplir tous les champs")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Connexion...")
        self.error_label.hide()

        try:
            if self.auth.login(email, password):
                self.logged_in.emit(self.auth.current_user)
                self.accept()
            else:
                self.show_error("Connexion échouée")
        except AuthError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"Erreur: {e}")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Connexion")

    def do_register(self):
        """Effectue l'inscription."""
        email = self.reg_email.text().strip()
        username = self.reg_username.text().strip()
        fullname = self.reg_fullname.text().strip()
        password = self.reg_password.text()
        password2 = self.reg_password2.text()

        # Validations
        if not all([email, username, fullname, password, password2]):
            self.show_error("Veuillez remplir tous les champs")
            return

        if len(username) < 3:
            self.show_error("Le nom d'utilisateur doit contenir au moins 3 caractères")
            return

        if len(password) < 8:
            self.show_error("Le mot de passe doit contenir au moins 8 caractères")
            return

        if password != password2:
            self.show_error("Les mots de passe ne correspondent pas")
            return

        self.register_btn.setEnabled(False)
        self.register_btn.setText("Création...")
        self.error_label.hide()

        try:
            user = self.auth.register(email, username, password, fullname)

            # Connexion automatique après inscription
            QMessageBox.information(
                self,
                "Compte créé",
                f"Bienvenue {user.full_name} !\n\nVous pouvez maintenant vous connecter."
            )

            # Passer à l'onglet connexion et pré-remplir
            self.tabs.setCurrentIndex(0)
            self.login_email.setText(email)
            self.login_password.setFocus()

        except AuthError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"Erreur: {e}")
        finally:
            self.register_btn.setEnabled(True)
            self.register_btn.setText("Créer le compte")

    def show_reset_dialog(self):
        """Affiche le dialog de reset password."""
        dialog = PasswordResetDialog(self.auth, self)
        dialog.exec()

    def show_error(self, message: str):
        """Affiche un message d'erreur."""
        self.error_label.setText(message)
        self.error_label.show()


class ProfileDialog(QDialog):
    """
    Dialog de profil utilisateur.

    Affiche et permet de modifier :
    - Nom d'utilisateur
    - Nom complet
    - Changer le mot de passe
    """

    profile_updated = pyqtSignal(object)  # Émet UserProfile après modification

    def __init__(self, auth_manager: AuthManager, parent=None):
        super().__init__(parent)
        self.auth = auth_manager

        self.setWindowTitle("Mon profil")
        self.setMinimumWidth(400)
        self.setModal(True)

        self.setup_ui()
        self.load_profile()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Infos utilisateur
        info_group = QGroupBox("Informations")
        info_layout = QFormLayout(info_group)

        self.email_label = QLabel()
        self.email_label.setStyleSheet("color: gray;")
        info_layout.addRow("Email:", self.email_label)

        self.username_input = QLineEdit()
        info_layout.addRow("Nom d'utilisateur:", self.username_input)

        self.fullname_input = QLineEdit()
        info_layout.addRow("Nom complet:", self.fullname_input)

        self.role_label = QLabel()
        self.role_label.setStyleSheet("color: gray;")
        info_layout.addRow("Rôle:", self.role_label)

        layout.addWidget(info_group)

        # Changer mot de passe
        password_group = QGroupBox("Changer le mot de passe")
        password_layout = QFormLayout(password_group)

        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password.setPlaceholderText("Mot de passe actuel")
        password_layout.addRow("Actuel:", self.current_password)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Nouveau mot de passe (8+ caractères)")
        password_layout.addRow("Nouveau:", self.new_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Confirmer")
        password_layout.addRow("Confirmation:", self.confirm_password)

        layout.addWidget(password_group)

        # Message
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.hide()
        layout.addWidget(self.message_label)

        # Boutons
        buttons = QHBoxLayout()

        self.logout_btn = QPushButton("Déconnexion")
        self.logout_btn.setStyleSheet(
            "QPushButton { color: #f44336; }"
        )
        self.logout_btn.clicked.connect(self.do_logout)
        buttons.addWidget(self.logout_btn)

        buttons.addStretch()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; "
            "padding: 8px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.save_btn.clicked.connect(self.save_profile)
        buttons.addWidget(self.save_btn)

        layout.addLayout(buttons)

    def load_profile(self):
        """Charge les données du profil."""
        user = self.auth.current_user
        if user:
            self.email_label.setText(user.email or "Non défini")
            self.username_input.setText(user.username or "")
            self.fullname_input.setText(user.full_name)
            self.role_label.setText(user.role.capitalize())

    def save_profile(self):
        """Sauvegarde les modifications."""
        self.message_label.hide()

        # Vérifier s'il y a des changements
        user = self.auth.current_user
        changes = {}

        new_username = self.username_input.text().strip()
        if new_username and new_username != user.username:
            if len(new_username) < 3:
                self.show_message("Nom d'utilisateur trop court (3+ caractères)", error=True)
                return
            changes["username"] = new_username

        new_fullname = self.fullname_input.text().strip()
        if new_fullname and new_fullname != user.full_name:
            changes["full_name"] = new_fullname

        # Changement de mot de passe
        current_pw = self.current_password.text()
        new_pw = self.new_password.text()
        confirm_pw = self.confirm_password.text()

        if current_pw or new_pw or confirm_pw:
            if not current_pw:
                self.show_message("Entrez le mot de passe actuel", error=True)
                return
            if len(new_pw) < 8:
                self.show_message("Nouveau mot de passe trop court (8+ caractères)", error=True)
                return
            if new_pw != confirm_pw:
                self.show_message("Les mots de passe ne correspondent pas", error=True)
                return

            # Changer le mot de passe
            try:
                self.auth.change_password(current_pw, new_pw)
                self.show_message("Mot de passe changé", error=False)
                self.current_password.clear()
                self.new_password.clear()
                self.confirm_password.clear()
            except AuthError as e:
                self.show_message(str(e), error=True)
                return

        # Mettre à jour le profil
        if changes:
            try:
                updated = self.auth.update_profile(**changes)
                if updated:
                    self.profile_updated.emit(updated)
                    self.show_message("Profil mis à jour", error=False)
                    self.load_profile()
            except Exception as e:
                self.show_message(f"Erreur: {e}", error=True)
                return

        if not changes and not current_pw:
            self.show_message("Aucune modification", error=False)

    def do_logout(self):
        """Déconnexion."""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.auth.logout()
            self.accept()

    def show_message(self, text: str, error: bool = False):
        """Affiche un message."""
        if error:
            self.message_label.setStyleSheet(
                "color: #f44336; padding: 5px; background-color: #ffebee; "
                "border-radius: 4px;"
            )
        else:
            self.message_label.setStyleSheet(
                "color: #4CAF50; padding: 5px; background-color: #E8F5E9; "
                "border-radius: 4px;"
            )
        self.message_label.setText(text)
        self.message_label.show()


class PasswordResetDialog(QDialog):
    """Dialog de reset mot de passe."""

    def __init__(self, auth_manager: AuthManager, parent=None):
        super().__init__(parent)
        self.auth = auth_manager

        self.setWindowTitle("Mot de passe oublié")
        self.setMinimumWidth(350)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Description
        desc = QLabel(
            "Entrez votre adresse email.\n"
            "Un lien de réinitialisation vous sera envoyé."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(desc)

        # Email
        form = QFormLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        self.email_input.returnPressed.connect(self.request_reset)
        form.addRow("Email:", self.email_input)
        layout.addLayout(form)

        # Message
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.hide()
        layout.addWidget(self.message_label)

        # Boutons
        buttons = QHBoxLayout()

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)

        self.send_btn = QPushButton("Envoyer")
        self.send_btn.setDefault(True)
        self.send_btn.clicked.connect(self.request_reset)
        buttons.addWidget(self.send_btn)

        layout.addLayout(buttons)

    def request_reset(self):
        """Demande le reset."""
        email = self.email_input.text().strip()

        if not email:
            self.show_message("Entrez votre email", error=True)
            return

        self.send_btn.setEnabled(False)
        self.send_btn.setText("Envoi...")

        try:
            self.auth.request_password_reset(email)
            self.show_message(
                "Si cet email existe, un lien de réinitialisation a été envoyé.",
                error=False
            )
            self.send_btn.setText("Envoyé")
        except Exception as e:
            self.show_message(f"Erreur: {e}", error=True)
            self.send_btn.setEnabled(True)
            self.send_btn.setText("Envoyer")

    def show_message(self, text: str, error: bool = False):
        """Affiche un message."""
        if error:
            self.message_label.setStyleSheet(
                "color: #f44336; padding: 5px; margin-top: 10px;"
            )
        else:
            self.message_label.setStyleSheet(
                "color: #4CAF50; padding: 5px; margin-top: 10px;"
            )
        self.message_label.setText(text)
        self.message_label.show()

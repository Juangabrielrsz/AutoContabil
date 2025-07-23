from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QApplication,
    QFrame,
    QTabWidget,
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt
import sqlite3
import sys
import os
from app.main_window import MainWindow
from app.utils import get_writable_db_path, resource_path
from PyQt5.QtWidgets import QDesktopWidget


class LoginScreen(QWidget):
    login_sucesso = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Automação Contábil")
        self.setGeometry(100, 100, 420, 350)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # ✅ Ícone da janela
        icon_path = resource_path("app/assets/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # ✅ Estilo visual
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f4f4f4;
                font-family: Arial;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                background: white;  /* Campo branco */
            }
            QPushButton {
                background-color: #2e86de;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e5fa3;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                background: none;  /* 🔥 remove fundo cinza */
            }
            """
        )

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(40, 30, 40, 30)

        # ✅ Ícone grande centralizado acima do login
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        # ✅ Cabeçalho
        header = QLabel("AutoContabil - Login")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuário")
        self.usuario_input.returnPressed.connect(self.verificar_login)

        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.returnPressed.connect(self.verificar_login)

        self.login_btn = QPushButton("Entrar")
        self.login_btn.clicked.connect(self.verificar_login)

        layout.addWidget(QLabel("Usuário:"))
        layout.addWidget(self.usuario_input)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.senha_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def verificar_login(self):
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()

        conn = sqlite3.connect(get_writable_db_path())
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                senha TEXT NOT NULL
            )
            """
        )

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "1234")
            )
            conn.commit()

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha)
        )
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")


# Teste isolado
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec())

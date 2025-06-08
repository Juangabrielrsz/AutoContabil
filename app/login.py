from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import pyqtSignal
import sqlite3
import sys
from app.main_window import MainWindow


class LoginScreen(QWidget):
    login_sucesso = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Automação Contábil")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuário")

        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.Password)

        # Conecta o Enter dos dois campos ao método verificar_login
        self.usuario_input.returnPressed.connect(self.verificar_login)
        self.senha_input.returnPressed.connect(self.verificar_login)

        self.login_btn = QPushButton("Entrar")
        self.login_btn.clicked.connect(self.verificar_login)

        layout.addWidget(QLabel("Usuário:"))
        layout.addWidget(self.usuario_input)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.senha_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def verificar_login(self):
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()

        conn = sqlite3.connect("app/database.db")
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
            self.main_window = MainWindow()  # Instancia a sua MainWindow
            self.main_window.show()  # Mostra a MainWindow
            self.close()  # Fecha a janela de login
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")


# Para testar o widget isoladamente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec())

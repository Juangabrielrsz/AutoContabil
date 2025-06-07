from PyQt5.QtWidgets import QApplication
from app.login import LoginScreen
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tela_login = LoginScreen()
    tela_login.show()
    sys.exit(app.exec_())

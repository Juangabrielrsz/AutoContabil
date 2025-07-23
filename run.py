from PyQt5.QtWidgets import QApplication
import sys
from app.login import LoginScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Estilo moderno global
    style_sheet = """
        QWidget {
            font-family: 'Segoe UI', sans-serif;
            font-size: 10pt;
            background-color: #f8f9fa;
            color: #212529;
        }

        QLabel {
            font-weight: bold;
            color: #343a40;
        }

        QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
        }

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
            border: 1px solid #5dade2;
            background-color: #ffffff;
        }

        QPushButton {
            background-color: #007bff;
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #0056b3;
        }

        QPushButton:disabled {
            background-color: #adb5bd;
            color: #f8f9fa;
        }

        QTableWidget {
            border: 1px solid #dee2e6;
            gridline-color: #dee2e6;
            background-color: white;
            alternate-background-color: #f1f3f5;
        }

        QHeaderView::section {
            background-color: #e9ecef;
            padding: 6px;
            border: 1px solid #dee2e6;
            font-weight: bold;
        }

        QScrollBar:vertical {
            background: #f1f1f1;
            width: 12px;
            margin: 0px;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical {
            background: #adb5bd;
            min-height: 20px;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical:hover {
            background: #6c757d;
        }

        QMessageBox {
            background-color: #ffffff;
        }
    """
    app.setStyleSheet(style_sheet)

    login = LoginScreen()
    login.show()
    sys.exit(app.exec())

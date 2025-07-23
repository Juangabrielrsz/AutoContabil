from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDesktopWidget
from app.tabs.tabs_notas_fiscais import TabsNotasFiscais
from app.tabs.tabs_extratos import TabsExtratos
from app.tabs.tabs_mei import TabsMei
from app.tabs.tabs_fechamento import TabsFechamento
from app.tabs.tabs_dp import TabsDP
from app.tabs.tabs_relatorios import TabsRelatorios
from app.utils import resource_path
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação Contábil")
        self.setGeometry(200, 200, 1000, 700)
        # ✅ Ícone da janela
        icon_path = resource_path("app/assets/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1280, 920)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Estilo para abas com largura mínima aumentada
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background: #ffffff;
            }

            QTabBar::tab {
                background: #f1f3f5;
                border: 1px solid #dee2e6;
                padding: 7px 15px;
                font-weight: bold;
                color: #495057;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 135px;  /* ← aumenta largura mínima das abas */
                max-width: 240px;
            }

            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
            }

            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """
        )

        # Abas
        self.tabs.addTab(TabsNotasFiscais(), "Notas Fiscais")
        self.tabs.addTab(TabsExtratos(), "Extratos")
        self.tabs.addTab(TabsMei(), "MEI")
        self.tabs.addTab(TabsFechamento(), "Fechamento Contábil")
        self.tabs.addTab(TabsDP(), "Departamento Pessoal")
        self.tabs.addTab(TabsRelatorios(), "Relatórios")

    def criar_aba(self, nome):
        aba = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Tela de {nome} (em construção)"))
        aba.setLayout(layout)
        return aba

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from app.tabs.tabs_notas_fiscais import TabsNotasFiscais
from app.tabs.tabs_extratos import TabsExtratos
from app.tabs.tabs_mei import TabsMei
from app.tabs.tabs_fechamento import TabsFechamento
from app.tabs.tabs_dp import TabsDP


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação Contábil")
        self.setGeometry(200, 200, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(TabsNotasFiscais(), "Notas Fiscais")
        self.tabs.addTab(TabsExtratos(), "Extratos")
        self.tabs.addTab(TabsMei(), "Mei")
        self.tabs.addTab(TabsFechamento(), "Fechamento Contábil")
        self.tabs.addTab(TabsDP(), "Departamento Pessoal")
        # Outras abas com placeholder "em construção"
        self.tabs.addTab(self.criar_aba("Relatórios"), "Relatórios")

    def criar_aba(self, nome):
        aba = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Tela de {nome} (em construção)"))
        aba.setLayout(layout)
        return aba

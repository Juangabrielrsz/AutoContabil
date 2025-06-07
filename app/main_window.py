from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from app.tabs.tabs_notas_fiscais import TabsNotasFiscais

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação Contábil")
        self.setGeometry(200, 200, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Aba Notas Fiscais
        self.tabs.addTab(TabsNotasFiscais(), "Notas Fiscais")
        # Outras abas com placeholder "em construção"
        self.tabs.addTab(self.criar_aba("Extratos Bancários"), "Extratos")
        self.tabs.addTab(self.criar_aba("Fechamento Contábil"), "Fechamento")
        self.tabs.addTab(self.criar_aba("Departamento Pessoal"), "Dept. Pessoal")
        self.tabs.addTab(self.criar_aba("Relatórios"), "Relatórios")

    def criar_aba(self, nome):
        aba = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Tela de {nome} (em construção)"))
        aba.setLayout(layout)
        return aba

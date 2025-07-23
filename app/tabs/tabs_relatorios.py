from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QHBoxLayout,
)
import sqlite3
from app.utils import get_writable_db_path


class TabsRelatorios(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Grupo de informações
        grupo_info = QGroupBox("📊 Relatórios de Cadastro")
        grupo_layout = QHBoxLayout()

        # Labels
        self.label_colaboradores = QLabel("Total de Colaboradores: 0")
        self.label_meis = QLabel("Total de MEIs: 0")

        self.label_colaboradores.setStyleSheet("font-size: 16px;")
        self.label_meis.setStyleSheet("font-size: 16px;")

        grupo_layout.addWidget(self.label_colaboradores)
        grupo_layout.addWidget(self.label_meis)

        grupo_info.setLayout(grupo_layout)
        layout.addWidget(grupo_info)

        self.setLayout(layout)
        self.atualizar_contadores()

    def atualizar_contadores(self):
        try:

            conn = sqlite3.connect(get_writable_db_path())
            cursor = conn.cursor()

            # Contar colaboradores
            cursor.execute("SELECT COUNT(*) FROM colaboradores")
            total_colabs = cursor.fetchone()[0]

            # Contar MEIs
            cursor.execute("SELECT COUNT(*) FROM mei")
            total_meis = cursor.fetchone()[0]

            conn.close()

            self.label_colaboradores.setText(
                f"👥 Total de Colaboradores: {total_colabs}"
            )
            self.label_meis.setText(f"🧾 Total de MEIs: {total_meis}")

        except Exception as e:
            self.label_colaboradores.setText("Erro ao carregar colaboradores")
            self.label_meis.setText("Erro ao carregar MEIs")
            print("Erro ao atualizar contadores:", e)

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QWidget,
    QFormLayout,
    QDoubleSpinBox,
    QDateEdit,
)
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QSizePolicy
from app.tabs.gerar_pdf_holerite import gerar_pdf_holerite
import sqlite3
from reportlab.lib.pagesizes import A4
from app.utils import get_writable_db_path


class FolhasGeradasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Folhas de Pagamento Geradas")
        self.resize(800, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels(
            [
                "Nome",
                "CPF",
                "Cargo",
                "Salário Base",
                "Data",
                "Benefícios",
                "Descontos",
                "Líquido",
                "Ações",
            ]
        )
        layout.addWidget(self.tabela)
        self.tabela.verticalHeader().setDefaultSectionSize(40)

        self.carregar_dados()

    def carregar_dados(self):
        conn = sqlite3.connect(get_writable_db_path())
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome, cpf, cargo, salario_base, data_pagamento,
                   beneficios, descontos, salario_liquido
            FROM folha_pagamento
        """
        )
        folhas = cursor.fetchall()
        conn.close()

        self.tabela.setRowCount(len(folhas))

        for i, folha in enumerate(folhas):
            for j, valor in enumerate(folha[1:]):
                item = QTableWidgetItem(str(valor))
                self.tabela.setItem(i, j, item)

            btn_editar = QPushButton("Editar")
            btn_excluir = QPushButton("Excluir")
            btn_exportar = QPushButton("Exportar PDF")

            # Tamanhos mínimos
            btn_editar.setMinimumWidth(90)
            btn_excluir.setMinimumWidth(90)
            btn_exportar.setMinimumWidth(110)

            # Layout de botões
            acoes_layout = QHBoxLayout()
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            acoes_layout.setSpacing(5)
            acoes_layout.addWidget(btn_editar)
            acoes_layout.addWidget(btn_excluir)
            acoes_layout.addWidget(btn_exportar)

            container = QWidget()
            container.setLayout(acoes_layout)

            # Força o widget a expandir horizontalmente
            container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            self.tabela.setCellWidget(i, 8, container)
            self.tabela.setColumnWidth(8, 360)

            btn_editar.clicked.connect(lambda _, r=folha: self.editar_folha(r))
            btn_excluir.clicked.connect(lambda _, id=folha[0]: self.excluir_folha(id))
            btn_exportar.clicked.connect(lambda _, r=folha: self.exportar_pdf(r))

            acoes_layout = QHBoxLayout()
            acoes_layout.addWidget(btn_editar)
            acoes_layout.addWidget(btn_excluir)
            acoes_layout.addWidget(btn_exportar)

            container = QWidget()
            container.setLayout(acoes_layout)
            self.tabela.setCellWidget(i, 8, container)
            self.tabela.setColumnWidth(8, 350)

    def editar_folha(self, folha):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Folha de Pagamento")
        layout = QFormLayout(dialog)

        input_salario = QDoubleSpinBox()
        input_salario.setMaximum(100000)
        input_salario.setValue(float(folha[4]))  # salário_base

        input_beneficios = QDoubleSpinBox()
        input_beneficios.setMaximum(100000)
        input_beneficios.setValue(float(folha[6]))  # benefícios

        input_descontos = QDoubleSpinBox()
        input_descontos.setMaximum(100000)
        input_descontos.setValue(float(folha[7]))  # descontos

        input_data = QDateEdit()
        input_data.setCalendarPopup(True)
        input_data.setDate(QDate.fromString(folha[5], "yyyy-MM-dd"))

        btn_salvar = QPushButton("Salvar")

        layout.addRow("Salário Base:", input_salario)
        layout.addRow("Benefícios:", input_beneficios)
        layout.addRow("Descontos:", input_descontos)
        layout.addRow("Data de Pagamento:", input_data)
        layout.addRow(btn_salvar)

        def salvar_alteracoes():
            salario = input_salario.value()
            beneficios = input_beneficios.value()
            descontos = input_descontos.value()
            data_pagamento = input_data.date().toString("yyyy-MM-dd")
            liquido = salario + beneficios - descontos

            conn = sqlite3.connect(get_writable_db_path())
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE folha_pagamento
                SET salario_base = ?, beneficios = ?, descontos = ?, data_pagamento = ?, salario_liquido = ?
                WHERE id = ?
                """,
                (salario, beneficios, descontos, data_pagamento, liquido, folha[0]),
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Folha atualizada com sucesso.")
            dialog.accept()
            self.carregar_dados()

        btn_salvar.clicked.connect(salvar_alteracoes)
        dialog.exec_()

    def excluir_folha(self, folha_id):
        confirm = QMessageBox.question(
            self, "Confirmação", "Deseja excluir esta folha?"
        )
        if confirm == QMessageBox.Yes:

            conn = sqlite3.connect(get_writable_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM folha_pagamento WHERE id = ?", (folha_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Excluído", "Folha removida.")
            self.carregar_dados()

    def exportar_pdf(self, folha):
        # Obter dados adicionais do colaborador
        conn = sqlite3.connect(get_writable_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT empresa, escritorio, data_admissao, cargo FROM colaboradores WHERE nome = ? AND cpf = ?",
            (folha[1], folha[2]),
        )
        colaborador_info = cursor.fetchone()
        conn.close()

        if not colaborador_info:
            QMessageBox.warning(self, "Erro", "Dados do colaborador não encontrados.")
            return

        empresa, escritorio, data_admissao, cargo = colaborador_info

        folha_dict = {
            "nome": folha[1],
            "cpf": folha[2],
            "cargo": cargo or folha[3],
            "salario_base": folha[4],
            "data_pagamento": folha[5],
            "beneficios": folha[6],
            "descontos": folha[7],
            "salario_liquido": folha[8],
            "dias_trabalhados": (folha[9] if len(folha) > 9 else "30"),
            "data_admissao": data_admissao,
            "empresa": empresa,
            "escritorio": escritorio,
        }

        # Chama a função de geração
        gerar_pdf_holerite(folha_dict)

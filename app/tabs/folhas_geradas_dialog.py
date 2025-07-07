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
import sqlite3
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


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
        conn = sqlite3.connect("app/database.db")
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

            conn = sqlite3.connect("app/database.db")
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
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM folha_pagamento WHERE id = ?", (folha_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Excluído", "Folha removida.")
            self.carregar_dados()

    def exportar_pdf(self, folha):
        nome_arquivo = f"holerite_{folha[1].replace(' ', '_')}_{folha[5]}.pdf"
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4
        y = altura - 30 * mm

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30 * mm, y, "Recibo de Pagamento de Salário")

        y -= 15 * mm
        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, f"Nome: {folha[1]}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"CPF: {folha[2]}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Cargo: {folha[3]}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Data de Pagamento: {folha[5]}")

        y -= 15 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30 * mm, y, "Demonstrativo de Pagamento")

        y -= 10 * mm
        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, f"Salário Base: R$ {folha[4]:,.2f}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Benefícios: R$ {folha[6]:,.2f}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Descontos: R$ {folha[7]:,.2f}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Salário Líquido: R$ {folha[8]:,.2f}")

        y -= 20 * mm
        c.drawString(
            30 * mm, y, "Assinatura do Funcionário: ____________________________"
        )

        c.save()
        QMessageBox.information(
            self, "Exportado", f"Holerite salvo como: {nome_arquivo}"
        )

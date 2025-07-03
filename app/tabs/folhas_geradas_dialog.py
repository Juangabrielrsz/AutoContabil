from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QWidget,
    QFileDialog,
)
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

    def editar_folha(self, folha):
        QMessageBox.information(
            self, "Aviso", "Funcionalidade de edição ainda será implementada."
        )

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

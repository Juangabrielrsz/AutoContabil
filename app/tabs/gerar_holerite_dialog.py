# gerar_holerite_dialog.py

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
    QDateEdit,
    QDoubleSpinBox,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import QDate
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


class GerarHoleriteDialog(QDialog):
    def __init__(self, colaborador_data, parent=None):
        super().__init__(parent)
        self.colaborador_data = colaborador_data
        self.setWindowTitle("Gerar Holerite")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.nome = QLabel(self.colaborador_data[1])
        self.cpf = QLabel(self.colaborador_data[2])
        self.cargo = QLabel(self.colaborador_data[4])
        self.salario_base = QLabel(
            f"R$ {self.colaborador_data[5]:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        self.data_pagamento = QDateEdit()
        self.data_pagamento.setCalendarPopup(True)
        self.data_pagamento.setDate(QDate.currentDate())

        self.beneficios = QDoubleSpinBox()
        self.beneficios.setPrefix("R$ ")
        self.beneficios.setMaximum(999999.99)
        self.beneficios.setDecimals(2)

        self.descontos = QDoubleSpinBox()
        self.descontos.setPrefix("R$ ")
        self.descontos.setMaximum(999999.99)
        self.descontos.setDecimals(2)

        form.addRow("Nome:", self.nome)
        form.addRow("CPF:", self.cpf)
        form.addRow("Cargo:", self.cargo)
        form.addRow("Salário Base:", self.salario_base)
        form.addRow("Data Pagamento:", self.data_pagamento)
        form.addRow("Benefícios:", self.beneficios)
        form.addRow("Descontos:", self.descontos)

        layout.addLayout(form)

        btn_gerar = QPushButton("Gerar Holerite")
        btn_gerar.clicked.connect(self.gerar_holerite)
        layout.addWidget(btn_gerar)

        self.setLayout(layout)

    def gerar_holerite(self):
        nome = self.colaborador_data[1]
        cpf = self.colaborador_data[2]
        cargo = self.colaborador_data[4]
        salario_base = float(self.colaborador_data[5])
        data_pagamento = self.data_pagamento.date().toString("yyyy-MM-dd")
        beneficios = float(self.beneficios.value())
        descontos = float(self.descontos.value())
        salario_liquido = salario_base + beneficios - descontos

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO folha_pagamento (
                colaborador_id, nome, cpf, cargo, salario_base,
                data_pagamento, beneficios, descontos, salario_liquido
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.colaborador_data[0],
                nome,
                cpf,
                cargo,
                salario_base,
                data_pagamento,
                beneficios,
                descontos,
                salario_liquido,
            ),
        )
        conn.commit()
        conn.close()

        self.gerar_pdf(
            nome,
            cpf,
            cargo,
            salario_base,
            data_pagamento,
            beneficios,
            descontos,
            salario_liquido,
        )
        QMessageBox.information(self, "Sucesso", "Holerite gerado e salvo com sucesso.")
        self.accept()

    def gerar_pdf(
        self,
        nome,
        cpf,
        cargo,
        salario_base,
        data_pagamento,
        beneficios,
        descontos,
        salario_liquido,
    ):
        arquivo = f"holerite_{nome.replace(' ', '_')}_{data_pagamento}.pdf"
        c = canvas.Canvas(arquivo, pagesize=A4)
        largura, altura = A4
        y = altura - 30 * mm

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(largura / 2, y, "RECIBO DE PAGAMENTO DE SALÁRIO")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, f"Nome: {nome}")
        y -= 12
        c.drawString(30 * mm, y, f"CPF: {cpf}")
        y -= 12
        c.drawString(30 * mm, y, f"Cargo: {cargo}")
        y -= 12
        c.drawString(30 * mm, y, f"Data de Pagamento: {data_pagamento}")
        y -= 12

        c.setFont("Helvetica-Bold", 10)
        y -= 10
        c.drawString(30 * mm, y, "Vencimentos")
        y -= 12
        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, f"Salário Base: R$ {salario_base:,.2f}")
        y -= 12
        c.drawString(30 * mm, y, f"Benefícios: R$ {beneficios:,.2f}")
        y -= 12
        c.drawString(30 * mm, y, f"Descontos: R$ {descontos:,.2f}")
        y -= 12
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30 * mm, y, f"Salário Líquido: R$ {salario_liquido:,.2f}")
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, "___________________________________________")
        y -= 12
        c.drawString(30 * mm, y, "Assinatura do Funcionário")

        c.save()

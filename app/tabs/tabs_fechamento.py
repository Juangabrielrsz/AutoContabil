from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QTextEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import QDate
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


class TabsFechamento(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Filtros de data
        filtro_layout = QHBoxLayout()
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())

        btn_gerar = QPushButton("Gerar Fechamento")
        btn_gerar.clicked.connect(self.gerar_fechamento)

        filtro_layout.addWidget(QLabel("Data Início:"))
        filtro_layout.addWidget(self.data_inicio)
        filtro_layout.addWidget(QLabel("Data Fim:"))
        filtro_layout.addWidget(self.data_fim)
        filtro_layout.addWidget(btn_gerar)

        layout.addLayout(filtro_layout)

        # Labels de resumo
        self.label_receitas = QLabel("Receitas: R$ 0,00")
        self.label_despesas = QLabel("Despesas: R$ 0,00")
        self.label_lucro = QLabel("Lucro/Prejuízo: R$ 0,00")
        self.label_impostos = QLabel("Impostos Estimados: R$ 0,00")
        self.label_saldo = QLabel("Saldo Final: R$ 0,00")

        layout.addWidget(self.label_receitas)
        layout.addWidget(self.label_despesas)
        layout.addWidget(self.label_lucro)
        layout.addWidget(self.label_impostos)
        layout.addWidget(self.label_saldo)

        # Comentário
        layout.addWidget(QLabel("Comentários do Contador:"))
        self.comentarios = QTextEdit()
        layout.addWidget(self.comentarios)

        # Botões de exportação
        botoes_exportacao = QHBoxLayout()
        btn_exportar_pdf = QPushButton("Exportar para PDF")
        btn_exportar_excel = QPushButton("Exportar para Excel")

        btn_exportar_pdf.clicked.connect(self.exportar_para_pdf)
        btn_exportar_excel.clicked.connect(self.exportar_excel)

        botoes_exportacao.addWidget(btn_exportar_pdf)
        botoes_exportacao.addWidget(btn_exportar_excel)
        layout.addLayout(botoes_exportacao)

        self.setLayout(layout)

    def gerar_fechamento(self):
        data_ini = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tipo, valor FROM extratos 
            WHERE data BETWEEN ? AND ?
        """,
            (data_ini, data_fim),
        )
        dados = cursor.fetchall()
        conn.close()

        total_receitas = sum(float(v) for t, v in dados if t == "Entrada")
        total_despesas = sum(float(v) for t, v in dados if t == "Saída")
        lucro = total_receitas - total_despesas

        # Imposto estimado (exemplo: 6% sobre receitas)
        impostos = total_receitas * 0.06
        saldo_final = lucro - impostos

        self.label_receitas.setText(f"Receitas: R$ {total_receitas:,.2f}")
        self.label_despesas.setText(f"Despesas: R$ {total_despesas:,.2f}")
        self.label_lucro.setText(f"Lucro/Prejuízo: R$ {lucro:,.2f}")
        self.label_impostos.setText(f"Impostos Estimados: R$ {impostos:,.2f}")
        self.label_saldo.setText(f"Saldo Final: R$ {saldo_final:,.2f}")

    def exportar_pdf(self):
        QMessageBox.information(
            self, "PDF", "Função de exportar para PDF ainda será implementada."
        )

    def exportar_excel(self):
        data_ini = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("app/database.db")
        df = pd.read_sql_query(
            "SELECT * FROM extratos WHERE data BETWEEN ? AND ?",
            conn,
            params=(data_ini, data_fim),
        )
        conn.close()

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar como Excel", "fechamento.xlsx", "Excel Files (*.xlsx)"
        )
        if caminho:
            df.to_excel(caminho, index=False)
            QMessageBox.information(
                self, "Exportado", f"Fechamento exportado para {caminho}"
            )

    def exportar_para_pdf(self):
        from datetime import datetime

        # Coletar dados do fechamento
        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")
        entradas = self.label_entradas.text().split("R$")[-1].strip()
        saidas = self.label_saidas.text().split("R$")[-1].strip()
        saldo = self.label_saldo.text().split("R$")[-1].strip()
        lucro = self.label_lucro.text().split("R$")[-1].strip()
        impostos = self.label_impostos.text().split("R$")[-1].strip()
        comentario = self.text_comentario.toPlainText()

        nome_arquivo = f"fechamento_{data_inicio}_a_{data_fim}.pdf".replace(":", "-")
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4

        y = altura - 30 * mm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30 * mm, y, "Fechamento Contábil")

        y -= 10 * mm
        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, f"Período: {data_inicio} a {data_fim}")

        y -= 10 * mm
        c.drawString(30 * mm, y, f"Total de Receitas: R$ {entradas}")
        y -= 7 * mm
        c.drawString(30 * mm, y, f"Total de Despesas: R$ {saidas}")
        y -= 7 * mm
        c.drawString(30 * mm, y, f"Lucro/Prejuízo: R$ {lucro}")
        y -= 7 * mm
        c.drawString(30 * mm, y, f"Impostos Estimados: R$ {impostos}")
        y -= 7 * mm
        c.drawString(30 * mm, y, f"Saldo Final: R$ {saldo}")

        y -= 15 * mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30 * mm, y, "Comentários do Contador:")

        y -= 7 * mm
        c.setFont("Helvetica", 10)
        for linha in comentario.split("\n"):
            c.drawString(30 * mm, y, linha)
        y -= 6 * mm

        c.save()

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
    QLineEdit,
    QCompleter,
)
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt
import sqlite3
import pandas as pd
from app.utils import get_writable_db_path


class TabsFechamento(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Filtros de data e cliente
        filtro_layout = QHBoxLayout()

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())

        # Campo de filtro por cliente ou CNPJ
        self.input_cliente_cnpj = QLineEdit()
        self.input_cliente_cnpj.setPlaceholderText("Digite nome do cliente ou CNPJ")
        self.input_cliente_cnpj.setMaximumWidth(220)

        # Autocomplete com nomes e CNPJs únicos

        conn = sqlite3.connect(get_writable_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cliente, cnpj FROM extratos")
        resultados = cursor.fetchall()
        conn.close()

        opcoes = set()
        for cliente, cnpj in resultados:
            if cliente:
                opcoes.add(cliente.strip())
            if cnpj:
                opcoes.add(cnpj.strip())
        completer = QCompleter(sorted(opcoes))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.input_cliente_cnpj.setCompleter(completer)

        btn_gerar = QPushButton("Gerar Fechamento")
        btn_gerar.clicked.connect(self.gerar_fechamento)

        filtro_layout.addWidget(QLabel("Data Início:"))
        filtro_layout.addWidget(self.data_inicio)
        filtro_layout.addWidget(QLabel("Data Fim:"))
        filtro_layout.addWidget(self.data_fim)
        filtro_layout.addWidget(QLabel("Cliente/CNPJ:"))
        filtro_layout.addWidget(self.input_cliente_cnpj)
        filtro_layout.addWidget(btn_gerar)

        layout.addLayout(filtro_layout)
        # Botões de exportação
        botoes_exportacao = QHBoxLayout()
        btn_exportar_pdf = QPushButton("Exportar para PDF")
        btn_exportar_excel = QPushButton("Exportar para Excel")

        btn_exportar_pdf.clicked.connect(self.exportar_para_pdf)
        btn_exportar_excel.clicked.connect(self.exportar_excel)

        botoes_exportacao.addWidget(btn_exportar_pdf)
        botoes_exportacao.addWidget(btn_exportar_excel)
        layout.addLayout(botoes_exportacao)

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

        # Comentários
        layout.addWidget(QLabel("Comentários do Contador:"))
        self.comentarios = QTextEdit()
        layout.addWidget(self.comentarios)

        self.setLayout(layout)

    def gerar_fechamento(self):
        data_ini = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")
        texto_filtro = self.input_cliente_cnpj.text().strip()

        conn = sqlite3.connect(get_writable_db_path())
        cursor = conn.cursor()

        query = "SELECT tipo, valor FROM extratos WHERE data BETWEEN ? AND ?"
        params = [data_ini, data_fim]

        if texto_filtro:
            query += " AND (cliente LIKE ? OR cnpj LIKE ?)"
            texto_busca = f"%{texto_filtro}%"
            params.extend([texto_busca, texto_busca])

        cursor.execute(query, params)
        dados = cursor.fetchall()
        conn.close()

        total_receitas = sum(float(v) for t, v in dados if t == "Entrada")
        total_despesas = sum(float(v) for t, v in dados if t == "Saída")
        lucro = total_receitas - total_despesas
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

        conn = sqlite3.connect(get_writable_db_path())
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
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from datetime import datetime
        import re

        # Coleta dos dados
        nome_cliente_cnpj = self.input_cliente_cnpj.text()
        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")
        receitas = self.label_receitas.text().split("R$")[-1].strip()
        despesas = self.label_despesas.text().split("R$")[-1].strip()
        lucro = self.label_lucro.text().split("R$")[-1].strip()
        impostos = self.label_impostos.text().split("R$")[-1].strip()
        saldo = self.label_saldo.text().split("R$")[-1].strip()
        comentario = self.comentarios.toPlainText()

        # Extrair CNPJ se possível
        cnpj_encontrado = re.search(
            r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", nome_cliente_cnpj
        )
        cnpj = cnpj_encontrado.group() if cnpj_encontrado else "sem_cnpj"

        # Nome do arquivo
        nome_arquivo = f"fechamento_{nome_cliente_cnpj.replace('/', '_').replace('.', '').replace(' ', '_')}_{data_inicio}_a_{data_fim}.pdf"

        # Criação do PDF
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4
        y = altura - 30 * mm

        c.setFont("Helvetica-Bold", 16)
        c.drawString(30 * mm, y, "Fechamento Contábil")

        y -= 10 * mm
        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, y, f"Cliente: {nome_cliente_cnpj}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Período: {data_inicio} a {data_fim}")

        y -= 10 * mm

        c.drawString(30 * mm, y, f"Receitas: R$ {receitas}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Despesas: R$ {despesas}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Lucro/Prejuízo: R$ {lucro}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Impostos Estimados: R$ {impostos}")
        y -= 6 * mm
        c.drawString(30 * mm, y, f"Saldo Final: R$ {saldo}")

        y -= 12 * mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30 * mm, y, "Comentários do Contador:")
        y -= 6 * mm

        c.setFont("Helvetica", 10)
        for linha in comentario.split("\n"):
            if y < 30 * mm:
                c.showPage()
                y = altura - 30 * mm
                c.setFont("Helvetica", 10)
                c.drawString(30 * mm, y, linha)
                y -= 5 * mm

            c.save()

        QMessageBox.information(
            self, "PDF Exportado", f"PDF gerado com sucesso:\n{nome_arquivo}"
        )

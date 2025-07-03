from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    QDialog,
    QFormLayout,
    QDateEdit,
    QDoubleSpinBox,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QDate
import sqlite3
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from app.tabs.folhas_geradas_dialog import FolhasGeradasDialog


class TabsDP(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Botões principais
        botoes_layout = QHBoxLayout()
        btn_adicionar = QPushButton("Adicionar Colaborador")
        btn_exportar_excel = QPushButton("Exportar Excel")
        btn_exportar_pdf = QPushButton("Exportar PDF")
        btn_ver_folhas = QPushButton("Ver Folhas Geradas")

        btn_adicionar.clicked.connect(self.abrir_dialogo_cadastro)
        btn_exportar_excel.clicked.connect(self.exportar_excel)
        btn_exportar_pdf.clicked.connect(self.exportar_pdf)
        btn_ver_folhas.clicked.connect(self.abrir_folhas_geradas)

        botoes_layout.addWidget(btn_adicionar)
        botoes_layout.addWidget(btn_exportar_excel)
        botoes_layout.addWidget(btn_exportar_pdf)
        botoes_layout.addWidget(btn_ver_folhas)
        layout.addLayout(botoes_layout)

        # Tabela de colaboradores
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(10)
        self.tabela.setHorizontalHeaderLabels(
            [
                "Nome",
                "CPF",
                "CNPJ Empresa",
                "Cargo",
                "Salário",
                "Tipo Contrato",
                "Admissão",
                "Demissão",
                "Observações",
                "Ações",
            ]
        )
        self.tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.carregar_dados()
        self.tabela.cellDoubleClicked.connect(self.abrir_detalhes_colaborador)

    def carregar_dados(self):
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome, cpf, cnpj_empresa, cargo, salario,
                   tipo_contrato, data_admissao, data_demissao, observacoes
            FROM colaboradores
        """
        )
        dados = cursor.fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            for j, value in enumerate(row[1:]):
                item = QTableWidgetItem(str(value) if value else "")
                self.tabela.setItem(i, j, item)

            # Botões
            btn_editar = QPushButton("Editar")
            btn_excluir = QPushButton("Excluir")
            btn_folha = QPushButton("Gerar Folha")

            btn_editar.setMinimumWidth(100)
            btn_excluir.setMinimumWidth(100)
            btn_folha.setMinimumWidth(140)

            btn_editar.clicked.connect(lambda _, r=row: self.abrir_dialogo_edicao(r))
            btn_excluir.clicked.connect(
                lambda _, id=row[0]: self.excluir_colaborador(id)
            )
            btn_folha.clicked.connect(lambda _, r=row: self.abrir_dialogo_folha(r))

            botoes_layout = QHBoxLayout()
            botoes_layout.addWidget(btn_editar)
            botoes_layout.addWidget(btn_excluir)
            botoes_layout.addWidget(btn_folha)
            botoes_layout.setContentsMargins(0, 0, 0, 0)

            cell_widget = QWidget()
            cell_widget.setLayout(botoes_layout)
            self.tabela.setCellWidget(i, 9, cell_widget)
            self.tabela.setColumnWidth(2, 160)
            self.tabela.setColumnWidth(9, 340)

    def abrir_dialogo_folha(self, colaborador):
        dialog = QDialog(self)
        dialog.setWindowTitle("Gerar Folha de Pagamento")
        layout = QFormLayout()

        input_data_pagamento = QDateEdit()
        input_data_pagamento.setCalendarPopup(True)
        input_data_pagamento.setDate(QDate.currentDate())

        input_beneficios = QDoubleSpinBox()
        input_beneficios.setPrefix("R$ ")
        input_beneficios.setMaximum(999999)

        input_descontos = QDoubleSpinBox()
        input_descontos.setPrefix("R$ ")
        input_descontos.setMaximum(999999)

        layout.addRow("Data de Pagamento:", input_data_pagamento)
        layout.addRow("Benefícios:", input_beneficios)
        layout.addRow("Descontos:", input_descontos)

        btn_salvar = QPushButton("Gerar Holerite")
        layout.addRow(btn_salvar)

        dialog.setLayout(layout)

        def gerar():
            data_pag = input_data_pagamento.date().toString("yyyy-MM-dd")
            beneficios = input_beneficios.value()
            descontos = input_descontos.value()
            salario_base = colaborador[5]
            salario_liquido = salario_base + beneficios - descontos

            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO folha_pagamento
                (colaborador_id, nome, cpf, cargo, salario_base, data_pagamento,
                beneficios, descontos, salario_liquido)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    colaborador[0],
                    colaborador[1],
                    colaborador[2],
                    colaborador[4],
                    salario_base,
                    data_pag,
                    beneficios,
                    descontos,
                    salario_liquido,
                ),
            )
            conn.commit()
            conn.close()

            self.gerar_pdf_holerite_detalhado(
                colaborador, data_pag, beneficios, descontos, salario_liquido
            )
            QMessageBox.information(
                self, "Sucesso", "Folha gerada e holerite exportado com sucesso."
            )
            dialog.accept()

        btn_salvar.clicked.connect(gerar)
        dialog.exec_()

    def gerar_pdf_holerite_detalhado(
        self, colaborador, data_pagamento, beneficios, descontos, salario_liquido
    ):
        from reportlab.lib.colors import black, grey

        nome_arquivo = (
            f"holerite_{colaborador[1].replace(' ', '_')}_{data_pagamento}.pdf"
        )
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4

        # Cabeçalho
        y = altura - 20 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, "EMPRESA EXEMPLO LTDA - ME")
        c.setFont("Helvetica", 9)
        c.drawString(20 * mm, y - 5 * mm, "CNPJ: 00.000.000/0001-00")
        c.drawString(100 * mm, y - 5 * mm, "CC: GERAL")
        c.drawString(100 * mm, y - 10 * mm, "Mensalista")
        c.drawString(160 * mm, y - 10 * mm, "Folha Mensal")
        c.drawString(160 * mm, y - 15 * mm, f"{data_pagamento[-7:]}")

        # Dados do funcionário
        y -= 25 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(20 * mm, y, f"{colaborador[1]}")
        c.setFont("Helvetica", 9)
        c.drawString(20 * mm, y - 5 * mm, f"{colaborador[4]}")
        c.drawString(100 * mm, y, "CBO: 422110")
        c.drawString(100 * mm, y - 5 * mm, "Departamento: 1")
        c.drawString(140 * mm, y - 5 * mm, "Filial: 1")
        c.drawString(100 * mm, y - 10 * mm, f"Admissão: {colaborador[7]}")

        # Tabela de Proventos e Descontos com linhas
        y -= 25 * mm
        c.setFont("Helvetica-Bold", 8)
        headers = ["Código", "Descrição", "Referência", "Vencimentos", "Descontos"]
        x_positions = [22, 40, 100, 120, 150]
        for i, header in enumerate(headers):
            c.drawString(x_positions[i] * mm, y, header)

        # Linhas da tabela
        y -= 6 * mm
        c.setStrokeColor(grey)
        c.line(20 * mm, y + 5 * mm, 190 * mm, y + 5 * mm)  # linha horizontal superior

        rubricas = [
            ("8781", "SALÁRIO", "30,00", f"{colaborador[5]:,.2f}", ""),
            ("995", "SALÁRIO FAMÍLIA", "31,71", f"{beneficios:,.2f}", ""),
            ("998", "INSS", "8,00", "", "87,56"),
            ("993", "DESCONTO", "0,54", "", f"{descontos:,.2f}"),
            ("048", "VALE TRANSPORTE", "6,00", "", "65,67"),
        ]

        c.setFont("Helvetica", 8)
        for i, (cod, desc, ref, venc, descs) in enumerate(rubricas):
            row_y = y - (i * 6 * mm)
            c.drawString(x_positions[0] * mm, row_y, cod)
            c.drawString(x_positions[1] * mm, row_y, desc)
            c.drawString(x_positions[2] * mm, row_y, ref)
            if venc:
                c.drawRightString((x_positions[3] + 20) * mm, row_y, venc)
            if descs:
                c.drawRightString((x_positions[4] + 30) * mm, row_y, descs)

            # Linha abaixo da linha atual
            c.line(20 * mm, row_y - 1 * mm, 190 * mm, row_y - 1 * mm)

        y = row_y - 10 * mm

        # Totais
        c.setFont("Helvetica-Bold", 8)
        c.drawString(100 * mm, y, "Total de Vencimentos:")
        c.drawRightString(145 * mm, y, f"{colaborador[5] + beneficios:,.2f}")
        y -= 5 * mm
        c.drawString(100 * mm, y, "Total de Descontos:")
        c.drawRightString(180 * mm, y, f"{descontos + 87.56 + 65.67:,.2f}")
        y -= 10 * mm
        c.drawString(100 * mm, y, "Valor Líquido:")
        c.drawRightString(180 * mm, y, f"{salario_liquido:,.2f}")

        # Bases de cálculo
        y -= 15 * mm
        c.setFont("Helvetica", 8)
        c.drawString(20 * mm, y, f"Salário Base: {colaborador[5]:,.2f}")
        c.drawString(60 * mm, y, f"Base INSS: {colaborador[5]:,.2f}")
        c.drawString(100 * mm, y, f"Base FGTS: {colaborador[5]:,.2f}")
        c.drawString(140 * mm, y, f"FGTS do mês: 87,56")

        y -= 6 * mm
        c.drawString(20 * mm, y, "Base IRRF: 817,35")
        c.drawString(60 * mm, y, "IRRF: 0,00")

        # Assinatura na mesma linha da data
        y -= 20 * mm
        c.drawString(20 * mm, y, "Assinatura do Funcionário:")
        c.line(60 * mm, y, 120 * mm, y)
        c.drawRightString(190 * mm, y, "Data: ____/____/______")

        c.save()

    def abrir_folhas_geradas(self):
        dialog = FolhasGeradasDialog(self)
        dialog.exec_()

    def abrir_dialogo_cadastro(self):
        QMessageBox.information(
            self, "Aviso", "Funcionalidade de cadastro em desenvolvimento."
        )

    def abrir_dialogo_edicao(self, colaborador):
        QMessageBox.information(
            self, "Aviso", "Funcionalidade de edição em desenvolvimento."
        )

    def excluir_colaborador(self, colaborador_id):
        resposta = QMessageBox.question(
            self, "Confirmação", "Tem certeza que deseja excluir este colaborador?"
        )
        if resposta == QMessageBox.Yes:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM colaboradores WHERE id = ?", (colaborador_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(
                self, "Excluído", "Colaborador excluído com sucesso."
            )
            self.carregar_dados()

    def exportar_excel(self):
        conn = sqlite3.connect("app/database.db")
        df = pd.read_sql_query("SELECT * FROM colaboradores", conn)
        conn.close()
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar como Excel", "", "Excel Files (*.xlsx)"
        )
        if caminho:
            df.to_excel(caminho, index=False)
            QMessageBox.information(self, "Exportado", "Dados exportados com sucesso.")

    def exportar_pdf(self):
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colaboradores")
        dados = cursor.fetchall()
        conn.close()
        nome_arquivo = "colaboradores.pdf"
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4
        y = altura - 30 * mm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30 * mm, y, "Lista de Colaboradores")
        y -= 10 * mm
        c.setFont("Helvetica", 8)
        for colab in dados:
            texto = (
                f"{colab[1]} - CPF: {colab[2]} - CNPJ: {colab[3]} - Cargo: {colab[4]}"
            )
            c.drawString(20 * mm, y, texto)
            y -= 6 * mm
            if y < 20 * mm:
                c.showPage()
                y = altura - 30 * mm
                c.setFont("Helvetica", 8)
        c.save()
        QMessageBox.information(self, "Exportado", "PDF gerado com sucesso.")

    def abrir_detalhes_colaborador(self, row, column):
        nome = self.tabela.item(row, 0).text()
        cpf = self.tabela.item(row, 1).text()
        cnpj = self.tabela.item(row, 2).text()
        cargo = self.tabela.item(row, 3).text()
        salario = self.tabela.item(row, 4).text()
        contrato = self.tabela.item(row, 5).text()
        admissao = self.tabela.item(row, 6).text()
        demissao = self.tabela.item(row, 7).text()
        obs = self.tabela.item(row, 8).text()

        detalhes = (
            f"👤 Nome: {nome}\n"
            f"🪪 CPF: {cpf}\n"
            f"🏢 CNPJ Empresa: {cnpj}\n"
            f"📌 Cargo: {cargo}\n"
            f"💰 Salário: R$ {salario}\n"
            f"📄 Tipo de Contrato: {contrato}\n"
            f"📆 Admissão: {admissao}\n"
            f"📆 Demissão: {demissao}\n"
            f"📝 Observações: {obs}"
        )

        QMessageBox.information(self, "Detalhes do Colaborador", detalhes)

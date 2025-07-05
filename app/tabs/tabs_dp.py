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
from app.tabs.colaborador_dialog import ColaboradorDialog


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
        self.tabela.setColumnCount(12)
        self.tabela.setHorizontalHeaderLabels(
            [
                "Nome",
                "CPF",
                "CNPJ Empresa",
                "Empresa",
                "Escritório",
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
            SELECT id, nome, cpf, cnpj_empresa, empresa, escritorio, cargo, salario,
                   tipo_contrato, data_admissao, data_demissao, observacoes
            FROM colaboradores
        """
        )
        dados = cursor.fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            for j, value in enumerate(row[1:11]):
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
            self.tabela.setCellWidget(i, 11, cell_widget)
            self.tabela.setColumnWidth(2, 160)
            self.tabela.setColumnWidth(11, 350)

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
            salario_base = float(colaborador[7])
            salario_liquido = salario_base + beneficios - descontos

            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO folha_pagamento
            (colaborador_id, nome, cpf, empresa, escritorio, cargo, salario_base, data_pagamento,
            beneficios, descontos, salario_liquido)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
                (
                    colaborador[0],  # id
                    colaborador[1],  # nome
                    colaborador[2],  # cpf
                    colaborador[4],  # empresa
                    colaborador[5],  # escritório
                    colaborador[6],  # cargo
                    salario_base,
                    data_pag,
                    beneficios,
                    descontos,
                    salario_liquido,
                ),
            )
            conn.commit()
            conn.close()
            print("Cargo:", colaborador[6])

            self.gerar_pdf_holerite_detalhado(
                colaborador,
                data_pag,
                beneficios,
                descontos,
                salario_liquido,
                salario_base,
            )
            QMessageBox.information(
                self, "Sucesso", "Folha gerada e holerite exportado com sucesso."
            )
            dialog.accept()

        btn_salvar.clicked.connect(gerar)
        dialog.exec_()

    def gerar_pdf_holerite_detalhado(
        self,
        colaborador,
        data_pagamento,
        beneficios,
        descontos,
        salario_liquido,
        salario_base,
    ):
        from reportlab.lib.colors import black, grey
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        import locale

        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        # Calcular INSS e IRRF
        def calcular_inss(salario):
            if salario <= 1302.00:
                return salario * 0.075
            elif salario <= 2571.29:
                return salario * 0.09
            elif salario <= 3856.94:
                return salario * 0.12
            elif salario <= 7507.49:
                return salario * 0.14
            else:
                return 7507.49 * 0.14  # teto

        def calcular_irrf(salario_base, inss):
            base_irrf = salario_base - inss
            if base_irrf <= 1903.98:
                return 0.0
            elif base_irrf <= 2826.65:
                return base_irrf * 0.075 - 142.80
            elif base_irrf <= 3751.05:
                return base_irrf * 0.15 - 354.80
            elif base_irrf <= 4664.68:
                return base_irrf * 0.225 - 636.13
            else:
                return base_irrf * 0.275 - 869.36

        inss = calcular_inss(salario_base)
        irrf = calcular_irrf(salario_base, inss)

        nome_arquivo = (
            f"holerite_{colaborador[1].replace(' ', '_')}_{data_pagamento}.pdf"
        )
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4

        y = altura - 20 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, colaborador[4])  # empresa
        c.setFont("Helvetica", 9)
        c.drawString(20 * mm, y - 5 * mm, "CNPJ: 00.000.000/0001-00")
        c.drawString(100 * mm, y - 5 * mm, "CC: GERAL")
        c.drawString(100 * mm, y - 10 * mm, "Mensalista")
        c.drawString(160 * mm, y - 10 * mm, "Folha Mensal")
        c.drawString(160 * mm, y - 15 * mm, f"{data_pagamento[-7:]}")

        y -= 25 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(20 * mm, y, f"{colaborador[1]}")  # nome
        c.setFont("Helvetica", 9)
        c.drawString(20 * mm, y - 5 * mm, f"{colaborador[6]}")  # cargo correto
        c.drawString(100 * mm, y, "CBO: 422110")
        c.drawString(100 * mm, y - 5 * mm, "Departamento: 1")
        c.drawString(140 * mm, y - 5 * mm, "Filial: 1")
        c.drawString(100 * mm, y - 10 * mm, f"Admissão: {data_pagamento}")

        # Cabeçalho da tabela
        y -= 25 * mm
        c.setFont("Helvetica-Bold", 8)
        headers = ["Código", "Descrição", "Referência", "Vencimentos", "Descontos"]
        x_positions = [22, 40, 100, 120, 150]
        for i, header in enumerate(headers):
            c.drawString(x_positions[i] * mm, y, header)

        y -= 6 * mm
        c.setStrokeColor(grey)
        c.line(20 * mm, y + 5 * mm, 190 * mm, y + 5 * mm)

        rubricas = [
            ("8781", "SALÁRIO", "30,00", f"{salario_base:,.2f}", ""),
            ("995", "SALÁRIO FAMÍLIA", "31,71", f"{beneficios:,.2f}", ""),
            ("998", "I.N.S.S.", "8,00", "", f"{inss:,.2f}"),
            ("993", "DESCONTO", "0,54", "", f"{descontos:,.2f}"),
            ("048", "VALE TRANSPORTE", "6,00", "", "65,67"),
            ("999", "IRRF", "Base IR", "", f"{irrf:,.2f}"),
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
            c.line(20 * mm, row_y - 1 * mm, 190 * mm, row_y - 1 * mm)

        y = row_y - 10 * mm
        total_venc = salario_base + beneficios
        total_desc = descontos + inss + irrf + 65.67

        c.setFont("Helvetica-Bold", 8)
        c.drawString(100 * mm, y, "Total de Vencimentos:")
        c.drawRightString(145 * mm, y, f"{total_venc:,.2f}")
        y -= 5 * mm
        c.drawString(100 * mm, y, "Total de Descontos:")
        c.drawRightString(180 * mm, y, f"{total_desc:,.2f}")
        y -= 10 * mm
        c.drawString(100 * mm, y, "Valor Líquido:")
        c.drawRightString(180 * mm, y, f"{salario_liquido:,.2f}")

        y -= 15 * mm
        c.setFont("Helvetica", 8)
        c.drawString(20 * mm, y, f"Salário Base: {salario_base:,.2f}")
        c.drawString(60 * mm, y, f"Base INSS: {salario_base:,.2f}")
        c.drawString(100 * mm, y, f"Base FGTS: {salario_base:,.2f}")
        c.drawString(140 * mm, y, "FGTS do mês: 87,56")
        y -= 6 * mm
        base_irrf = salario_base - inss
        c.drawString(20 * mm, y, f"Base IRRF: {base_irrf:,.2f}")
        c.drawString(60 * mm, y, f"IRRF: {irrf:,.2f}")
        y -= 20 * mm
        c.drawString(20 * mm, y, "Assinatura do Funcionário:")
        c.line(60 * mm, y, 120 * mm, y)
        c.drawRightString(190 * mm, y, "Data: ____/____/______")

        c.save()

    def abrir_folhas_geradas(self):
        dialog = FolhasGeradasDialog(self)
        dialog.exec_()

    def abrir_dialogo_cadastro(self):
        dialog = ColaboradorDialog(self)
        if dialog.exec_():
            self.carregar_dados()

    def abrir_dialogo_edicao(self, colaborador):
        dialog = ColaboradorDialog(self, colaborador)
        if dialog.exec_():
            self.carregar_dados()

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
        nome_item = self.tabela.item(row, 0)
        nome = nome_item.text() if nome_item else ""

        cpf_item = self.tabela.item(row, 1)
        cpf = cpf_item.text() if cpf_item else ""

        cnpj = self.tabela.item(row, 2).text()
        empresa = self.tabela.item(row, 3).text()
        escritorio = self.tabela.item(row, 4).text()
        cargo = self.tabela.item(row, 5).text()
        salario = self.tabela.item(row, 6).text()
        contrato = self.tabela.item(row, 7).text()
        admissao = self.tabela.item(row, 8).text()
        demissao = self.tabela.item(row, 9).text()
        obs_item = self.tabela.item(row, 10)
        obs = obs_item.text() if obs_item else ""

        detalhes = (
            f"<b>👤 Nome:</b> {nome}<br>"
            f"<b>🪪 CPF:</b> {cpf}<br>"
            f"<b>🏢 CNPJ Empresa:</b> {cnpj}<br>"
            f"<b>🏭 Empresa:</b> {empresa}<br>"
            f"<b>🏢 Escritório:</b> {escritorio}<br>"
            f"<b>📌 Cargo:</b> {cargo}<br>"
            f"<b>💰 Salário:</b> R$ {salario}<br>"
            f"<b>📄 Tipo de Contrato:</b> {contrato}<br>"
            f"<b>📆 Admissão:</b> {admissao}<br>"
            f"<b>📆 Demissão:</b> {demissao}<br>"
            f"<b>📝 Observações:</b><br>{obs}"
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Detalhes do Colaborador")
        msg.setTextFormat(Qt.RichText)
        msg.setText(detalhes)
        msg.exec_()

        QMessageBox.information(self, "Detalhes do Colaborador", detalhes)

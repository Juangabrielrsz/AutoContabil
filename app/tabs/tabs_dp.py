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
    QLineEdit,
    QLabel,
    QCompleter,
)
from PyQt5.QtCore import Qt, QDate
from app.tabs.gerar_pdf_holerite import gerar_pdf_holerite
import sqlite3
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from app.tabs.folhas_geradas_dialog import FolhasGeradasDialog
from app.tabs.colaborador_dialog import ColaboradorDialog
from PyQt5.QtWidgets import QCheckBox


class TabsDP(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Layout de filtros superiores
        filtro_layout = QHBoxLayout()

        # Filtro por Nome/CPF
        filtro_layout.addWidget(QLabel("Nome/CPF:"))
        self.input_nome_cpf = QLineEdit()
        self.input_nome_cpf.setPlaceholderText("Digite Nome ou CPF do Colaborador")
        self.input_nome_cpf.setMaximumWidth(220)
        filtro_layout.addWidget(self.input_nome_cpf)

        # Filtro por Nome da Empresa
        filtro_layout.addWidget(QLabel("Empresa:"))
        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Digite o nome da Empresa")
        self.input_empresa.setMaximumWidth(220)
        filtro_layout.addWidget(self.input_empresa)

        filtro_layout.addStretch()  # Empurra tudo para a esquerda

        # Autocomplete para Nome/CPF
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT nome, cpf FROM folha_pagamento")
        resultados = cursor.fetchall()

        opcoes_nome_cpf = set()
        for nome, cpf in resultados:
            if nome:
                opcoes_nome_cpf.add(nome.strip())
            if cpf:
                opcoes_nome_cpf.add(cpf.strip())

        completer_nome_cpf = QCompleter(sorted(opcoes_nome_cpf))
        completer_nome_cpf.setCaseSensitivity(Qt.CaseInsensitive)
        completer_nome_cpf.setFilterMode(Qt.MatchContains)
        self.input_nome_cpf.setCompleter(completer_nome_cpf)

        # Autocomplete para Empresa
        cursor.execute("SELECT DISTINCT empresa FROM colaboradores")
        empresas = [e[0] for e in cursor.fetchall() if e[0]]

        completer_empresa = QCompleter(sorted(empresas))
        completer_empresa.setCaseSensitivity(Qt.CaseInsensitive)
        completer_empresa.setFilterMode(Qt.MatchContains)
        self.input_empresa.setCompleter(completer_empresa)
        self.input_nome_cpf.textChanged.connect(self.carregar_dados)
        self.input_empresa.textChanged.connect(self.carregar_dados)
        conn.close()

        layout.addLayout(filtro_layout)

        opcoes = set()
        for nome, cpf in resultados:
            if nome:
                opcoes.add(nome.strip())
            if cpf:
                opcoes.add(cpf.strip())

        completer = QCompleter(sorted(opcoes))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.input_nome_cpf.setCompleter(completer)

        layout.addLayout(filtro_layout)

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

        # Tabela
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
        self.tabela.verticalHeader().setDefaultSectionSize(40)
        self.tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.carregar_dados()
        self.tabela.cellDoubleClicked.connect(self.abrir_detalhes_colaborador)

    def carregar_dados(self):
        nome_cpf_filtro = self.input_nome_cpf.text().strip()
        empresa_filtro = self.input_empresa.text().strip()

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()

        query = """
            SELECT id, nome, cpf, cnpj_empresa, empresa, escritorio, cargo, salario,
                tipo_contrato, data_admissao, data_demissao, observacoes
            FROM colaboradores
            WHERE 1 = 1
        """
        params = []

        if nome_cpf_filtro:
            query += " AND (nome LIKE ? OR cpf LIKE ?)"
            filtro = f"%{nome_cpf_filtro}%"
            params.extend([filtro, filtro])

        if empresa_filtro:
            query += " AND empresa LIKE ?"
            params.append(f"%{empresa_filtro}%")

        cursor.execute(query, params)
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

        input_dias_trabalhados = QDoubleSpinBox()
        input_dias_trabalhados.setMinimum(1)

        input_beneficios = QDoubleSpinBox()
        input_beneficios.setPrefix("R$ ")
        input_beneficios.setMaximum(999999)

        input_vale_refeicao = QDoubleSpinBox()
        input_vale_refeicao.setPrefix("R$ ")
        input_vale_refeicao.setMaximum(999999)

        input_vale_transporte = QDoubleSpinBox()
        input_vale_transporte.setPrefix("R$ ")
        input_vale_transporte.setMaximum(999999)

        input_atrasos_faltas = QDoubleSpinBox()
        input_atrasos_faltas.setPrefix("R$ ")
        input_atrasos_faltas.setMaximum(999999)

        input_descontos = QDoubleSpinBox()
        input_descontos.setPrefix("R$ ")
        input_descontos.setMaximum(999999)

        layout.addRow("Data de Pagamento:", input_data_pagamento)
        layout.addRow("Dias Trabalhados", input_dias_trabalhados := QDoubleSpinBox())
        layout.addRow("Benefícios:", input_beneficios)
        layout.addRow("Vale Refeição/Alimentação:", input_vale_refeicao)
        layout.addRow("Vale Transporte:", input_vale_transporte)
        layout.addRow("Atrasos/Faltas:", input_atrasos_faltas)
        layout.addRow("Outros Descontos:", input_descontos)

        btn_salvar = QPushButton("Gerar Holerite")
        layout.addRow(btn_salvar)
        dialog.setLayout(layout)

        def gerar():
            data_pag = input_data_pagamento.date().toString("yyyy-MM-dd")
            dias_trabalhados = input_dias_trabalhados.value()
            beneficios = input_beneficios.value()
            vale_refeicao = input_vale_refeicao.value()
            vale_transporte = input_vale_transporte.value()
            atrasos_faltas = input_atrasos_faltas.value()
            outros_descontos = input_descontos.value()

            salario_base = float(colaborador[7])

            # 🟡 APLICANDO REGRAS DE DESCONTO
            desconto_vale_refeicao = min(vale_refeicao, vale_refeicao * 0.20)
            desconto_vale_transporte = min(vale_transporte, salario_base * 0.06)

            # 🧮 Total de descontos
            total_descontos = (
                outros_descontos
                + atrasos_faltas
                + desconto_vale_refeicao
                + desconto_vale_transporte
            )

            # 🧾 Cálculo do salário líquido
            salario_liquido = (
                salario_base
                + beneficios
                + vale_refeicao
                + vale_transporte
                - total_descontos
            )

            # Salvar no banco
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
                    colaborador[0],
                    colaborador[1],
                    colaborador[2],
                    colaborador[4],
                    colaborador[5],
                    colaborador[6],
                    salario_base,
                    data_pag,
                    beneficios,
                    total_descontos,
                    salario_liquido,
                ),
            )
            conn.commit()
            conn.close()

            # Monta o dicionário para o PDF
            folha_dict = {
                "nome": colaborador[1],
                "cpf": colaborador[2],
                "cargo": colaborador[6],
                "salario_base": salario_base,
                "data_pagamento": data_pag,
                "beneficios": beneficios,
                "descontos": total_descontos,
                "salario_liquido": salario_liquido,
                "data_admissao": colaborador[9],
                "empresa": colaborador[4],
                "escritorio": colaborador[5],
                "dias_trabalhados": dias_trabalhados,
                "vale_refeicao": vale_refeicao,
                "vale_transporte": vale_transporte,
                "atrasos_faltas": atrasos_faltas,
                "outros_descontos": outros_descontos,
                "desconto_vale_refeicao": desconto_vale_refeicao,
                "desconto_vale_transporte": desconto_vale_transporte,
            }

            gerar_pdf_holerite(self, folha_dict)

            QMessageBox.information(
                self, "Sucesso", "Folha gerada e holerite exportado com sucesso."
            )
            dialog.accept()

        btn_salvar.clicked.connect(gerar)
        dialog.exec_()

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

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QDialog,
    QFormLayout,
    QMessageBox,
    QComboBox,
    QInputDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from functools import partial
import sqlite3


class TabsMei(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Define fonte maior
        fonte_maior = QFont()
        fonte_maior.setPointSize(8)

        # Filtro por nome ou CNPJ
        filtro_layout = QHBoxLayout()
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar por nome ou CNPJ...")
        self.input_filtro.setFont(fonte_maior)
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setFont(fonte_maior)
        btn_filtrar.clicked.connect(self.carregar_dados)
        filtro_layout.addWidget(self.input_filtro)
        filtro_layout.addWidget(btn_filtrar)
        layout.addLayout(filtro_layout)

        # Botão de cadastro
        btn_novo = QPushButton("Cadastrar Novo MEI")
        btn_novo.setFont(fonte_maior)
        btn_novo.clicked.connect(self.abrir_dialogo_cadastro)
        layout.addWidget(btn_novo)

        # Paginação
        self.pagina_atual_mei = 0
        self.registros_por_pagina_mei = 20
        self.total_paginas_mei = 0

        # Tabela de MEIs
        self.tabela = QTableWidget()
        self.tabela.setFont(fonte_maior)
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(
            [
                "Nome",
                "Email",
                "Senha Gov",
                "CNPJ",
                "CPF",
                "Código de Acesso",
                "Editar",
                "Excluir",
            ]
        )
        self.tabela.horizontalHeader().setFont(fonte_maior)
        self.tabela.verticalHeader().setDefaultSectionSize(35)
        layout.addWidget(self.tabela)
        self.tabela.setColumnWidth(1, 250)

        # CONTROLE DE EMISSÃO MEI
        self.label_controle = QLabel("Controle de Emissão MEI para o MEI selecionado:")
        self.label_controle.setFont(fonte_maior)
        layout.addWidget(self.label_controle)

        controle_layout = QHBoxLayout()

        self.combo_mes = QComboBox()
        self.combo_mes.setFont(fonte_maior)
        self.combo_mes.addItems([f"2025-{str(m).zfill(2)}" for m in range(1, 13)])

        self.input_valor_emitido = QLineEdit()
        self.input_valor_emitido.setFont(fonte_maior)
        self.input_valor_emitido.setPlaceholderText("Valor (ex: 1234.56)")

        self.btn_salvar_controle = QPushButton("Registrar Emissão")
        self.btn_salvar_controle.setFont(fonte_maior)
        self.btn_salvar_controle.clicked.connect(self.salvar_emissao)

        controle_layout.addWidget(QLabel("Mês:"))
        controle_layout.addWidget(self.combo_mes)
        controle_layout.addWidget(QLabel("Valor:"))
        controle_layout.addWidget(self.input_valor_emitido)
        controle_layout.addWidget(self.btn_salvar_controle)
        layout.addLayout(controle_layout)

        # Tabela de emissões
        self.tabela_emissoes = QTableWidget()
        self.tabela_emissoes.setFont(fonte_maior)
        self.tabela_emissoes.setColumnCount(5)
        self.tabela_emissoes.setHorizontalHeaderLabels(
            ["Mês", "Valor Emitido", "Acumulado no Ano", "Editar", "Excluir"]
        )
        self.tabela_emissoes.horizontalHeader().setFont(fonte_maior)
        self.tabela_emissoes.verticalHeader().setDefaultSectionSize(35)
        layout.addWidget(self.tabela_emissoes)

        # Navegação
        navegacao_layout = QHBoxLayout()
        self.btn_anterior_mei = QPushButton("Anterior")
        self.btn_anterior_mei.setFont(fonte_maior)
        self.btn_proximo_mei = QPushButton("Próximo")
        self.btn_proximo_mei.setFont(fonte_maior)
        self.btn_anterior_mei.clicked.connect(self.ir_para_anterior_mei)
        self.btn_proximo_mei.clicked.connect(self.ir_para_proximo_mei)
        navegacao_layout.addWidget(self.btn_anterior_mei)
        navegacao_layout.addWidget(self.btn_proximo_mei)
        layout.addLayout(navegacao_layout)

        self.setLayout(layout)
        self.carregar_dados()
        self.tabela.cellClicked.connect(self.atualizar_emissoes_por_linha)

    def atualizar_emissoes_por_linha(self, row, _column):
        # Obtém nome do MEI clicado
        mei_nome = self.tabela.item(row, 0).text()

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM mei WHERE nome = ?", (mei_nome,))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.carregar_emissoes(result[0])

    def carregar_dados(self):
        filtro = self.input_filtro.text().strip()
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()

        if filtro:
            cursor.execute(
                """
                SELECT rowid, nome, email, senha_gov, cnpj, cpf, codigo_acesso
                FROM mei 
                WHERE nome LIKE ? OR cnpj LIKE ?
                ORDER BY nome
            """,
                (f"%{filtro}%", f"%{filtro}%"),
            )
        else:
            cursor.execute(
                "SELECT rowid, nome, email, senha_gov, cnpj, cpf, codigo_acesso FROM mei ORDER BY nome"
            )

        todos_dados = cursor.fetchall()
        conn.close()

        total_registros = len(todos_dados)
        self.total_paginas_mei = (
            total_registros + self.registros_por_pagina_mei - 1
        ) // self.registros_por_pagina_mei

        inicio = self.pagina_atual_mei * self.registros_por_pagina_mei
        fim = inicio + self.registros_por_pagina_mei
        dados_pagina = todos_dados[inicio:fim]

        self.tabela.setRowCount(len(dados_pagina))

        for i, row in enumerate(dados_pagina):
            rowid, nome, email, senha, cnpj, cpf, codigo = row

            # Formatar CNPJ
            cnpj_limpo = "".join(filter(str.isdigit, cnpj))
            if len(cnpj_limpo) == 14:
                cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
            else:
                cnpj_formatado = cnpj
            cpf_limpo = "".join(filter(str.isdigit, cpf))
            if len(cpf_limpo) == 11:
                cpf_formatado = (
                    f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
                )
            else:
                cpf_formatado = cpf

            self.tabela.setItem(i, 0, QTableWidgetItem(nome))
            self.tabela.setItem(i, 1, QTableWidgetItem(email))
            self.tabela.setItem(i, 2, QTableWidgetItem(senha))
            self.tabela.setItem(i, 3, QTableWidgetItem(cnpj_formatado))
            self.tabela.setItem(i, 4, QTableWidgetItem(cpf_formatado))
            self.tabela.setItem(i, 5, QTableWidgetItem(codigo))

            # Botão Editar
            btn_editar = QPushButton("Editar")
            btn_editar.clicked.connect(
                lambda _, rid=rowid: self.abrir_dialogo_cadastro(editar_id=rid)
            )
            self.tabela.setCellWidget(i, 6, btn_editar)

            # Botão Excluir
            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda _, rid=rowid: self.excluir_mei(rid))
            self.tabela.setCellWidget(i, 7, btn_excluir)

        self.btn_anterior_mei.setEnabled(self.pagina_atual_mei > 0)
        self.btn_proximo_mei.setEnabled(
            self.pagina_atual_mei < self.total_paginas_mei - 1
        )

    def abrir_dialogo_cadastro(self, editar_id=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar MEI" if editar_id else "Cadastrar Novo MEI")
        layout = QFormLayout()

        input_nome = QLineEdit()
        input_email = QLineEdit()
        input_senha = QLineEdit()
        input_cnpj = QLineEdit()
        input_cnpj.setInputMask("00.000.000/0000-00")
        input_codigo = QLineEdit()
        input_cpf = QLineEdit()
        input_cpf.setInputMask("000.000.000-00")

        # Se edição, carregar dados existentes
        if editar_id:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nome, email, senha_gov, cnpj, cpf, codigo_acesso FROM mei WHERE rowid = ?",
                (editar_id,),
            )
            dados = cursor.fetchone()
            conn.close()
            if dados:
                input_nome.setText(dados[0])
                input_email.setText(dados[1])
                input_senha.setText(dados[2])
                input_cnpj.setText(dados[3])
                input_cpf.setText(dados[4])
                input_codigo.setText(dados[5])

        layout.addRow("Nome:", input_nome)
        layout.addRow("Email:", input_email)
        layout.addRow("Senha Gov:", input_senha)
        layout.addRow("CNPJ:", input_cnpj)
        layout.addRow("CPF:", input_cpf)
        layout.addRow("Código de Acesso:", input_codigo)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(
            lambda: self.salvar_mei(
                dialog,
                input_nome,
                input_email,
                input_senha,
                input_cnpj,
                input_cpf,
                input_codigo,
                editar_id,
            )
        )
        layout.addRow(btn_salvar)

        dialog.setLayout(layout)
        dialog.exec_()

    def salvar_mei(
        self, dialog, nome, email, senha, cnpj, cpf, codigo_acesso, editar_id=None
    ):
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        if editar_id:
            cursor.execute(
                "UPDATE mei SET nome = ?, email = ?, senha_gov = ?, cnpj = ?, cpf = ?, codigo_acesso = ? WHERE rowid = ?",
                (
                    nome.text(),
                    email.text(),
                    senha.text(),
                    cnpj.text(),
                    cpf.text(),
                    codigo_acesso.text(),
                    editar_id,
                ),
            )
        else:
            cursor.execute(
                "INSERT INTO mei (nome, email, senha_gov, cnpj, cpf, codigo_acesso) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    nome.text(),
                    email.text(),
                    senha.text(),
                    cnpj.text(),
                    cpf.text(),
                    codigo_acesso.text(),
                ),
            )
        conn.commit()
        conn.close()
        dialog.accept()
        self.carregar_dados()

    def excluir_mei(self, rowid):
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este MEI?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM mei WHERE rowid = ?", (rowid,))
            conn.commit()
            conn.close()
            self.carregar_dados()

    def ir_para_anterior_mei(self):
        if self.pagina_atual_mei > 0:
            self.pagina_atual_mei -= 1
            self.carregar_dados()

    def ir_para_proximo_mei(self):
        if self.pagina_atual_mei < self.total_paginas_mei - 1:
            self.pagina_atual_mei += 1
            self.carregar_dados()

    def salvar_emissao(self):
        selected_row = self.tabela.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Aviso", "Selecione um MEI na tabela principal.")
            return

        mei_nome = self.tabela.item(selected_row, 0).text()

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT rowid FROM mei WHERE nome = ?", (mei_nome,))
        result = cursor.fetchone()
        if not result:
            QMessageBox.warning(self, "Erro", "MEI não encontrado no banco de dados.")
            return

        mei_id = result[0]
        mes = self.combo_mes.currentText()
        try:
            valor = float(self.input_valor_emitido.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor inválido.")
            return

        cursor.execute(
            """
            INSERT INTO controle_emissao_mei (mei_id, mes, valor_emitido)
            VALUES (?, ?, ?)
            """,
            (mei_id, mes, valor),
        )
        conn.commit()

        # Verificar total anual
        ano = mes.split("-")[0]
        cursor.execute(
            """
            SELECT SUM(valor_emitido) FROM controle_emissao_mei
            WHERE mei_id = ? AND mes LIKE ?
            """,
            (mei_id, f"{ano}-%"),
        )
        total = cursor.fetchone()[0] or 0

        conn.close()

        if total > 81000:
            QMessageBox.warning(
                self,
                "Limite Excedido",
                f"O MEI selecionado ultrapassou o limite de R$ 81.000,00 no ano de {ano}.\nTotal: R$ {total:,.2f}".replace(
                    ",", "X"
                )
                .replace(".", ",")
                .replace("X", "."),
            )

        self.input_valor_emitido.clear()
        self.carregar_emissoes(mei_id)

    def carregar_emissoes(self, mei_id):
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT mes, valor_emitido FROM controle_emissao_mei
            WHERE mei_id = ?
            ORDER BY mes
            """,
            (mei_id,),
        )
        dados = cursor.fetchall()
        conn.close()

        acumulado = 0
        self.tabela_emissoes.setRowCount(len(dados))
        for i, (mes, valor) in enumerate(dados):
            acumulado += valor

            self.tabela_emissoes.setItem(i, 0, QTableWidgetItem(mes))
            self.tabela_emissoes.setItem(
                i,
                1,
                QTableWidgetItem(
                    f"R$ {valor:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                ),
            )
            self.tabela_emissoes.setItem(
                i,
                2,
                QTableWidgetItem(
                    f"R$ {acumulado:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                ),
            )

            # Botão Editar
            btn_editar = QPushButton("Editar")
            btn_editar.setMinimumWidth(70)
            btn_editar.clicked.connect(partial(self.editar_emissao, mei_id, mes, valor))
            self.tabela_emissoes.setCellWidget(i, 3, btn_editar)

            # Botão Excluir
            btn_excluir = QPushButton("Excluir")
            btn_excluir.setMinimumWidth(70)
            btn_excluir.clicked.connect(partial(self.excluir_emissao, mei_id, mes))
            self.tabela_emissoes.setCellWidget(i, 4, btn_excluir)
            self.tabela_emissoes.resizeColumnsToContents()
            self.tabela_emissoes.verticalHeader().setDefaultSectionSize(35)

    def editar_emissao(self, mei_id, mes, valor_atual):
        novo_valor, ok = QInputDialog.getDouble(
            self,
            "Editar Emissão",
            f"Novo valor para {mes}:",
            value=valor_atual,
            min=0.0,
            decimals=2,
        )
        if ok:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE controle_emissao_mei SET valor_emitido = ? WHERE mei_id = ? AND mes = ?",
                (novo_valor, mei_id, mes),
            )
            conn.commit()
            conn.close()
            self.carregar_emissoes(mei_id)

    def excluir_emissao(self, mei_id, mes):
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a emissão do mês {mes}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM controle_emissao_mei WHERE mei_id = ? AND mes = ?",
                (mei_id, mes),
            )
            conn.commit()
            conn.close()
            self.carregar_emissoes(mei_id)

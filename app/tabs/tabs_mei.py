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
)
from PyQt5.QtCore import Qt
import sqlite3


class TabsMei(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Filtro por nome ou CNPJ
        filtro_layout = QHBoxLayout()
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar por nome ou CNPJ...")
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.carregar_dados)
        filtro_layout.addWidget(self.input_filtro)
        filtro_layout.addWidget(btn_filtrar)
        layout.addLayout(filtro_layout)

        # Botão de cadastro
        btn_novo = QPushButton("Cadastrar Novo MEI")
        btn_novo.clicked.connect(self.abrir_dialogo_cadastro)
        layout.addWidget(btn_novo)

        # Paginação
        self.pagina_atual_mei = 0
        self.registros_por_pagina_mei = 20
        self.total_paginas_mei = 0

        # Tabela de MEIs
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["Nome", "Email", "Senha Gov", "CNPJ", "Editar", "Excluir"]
        )
        layout.addWidget(self.tabela)
        self.tabela.setColumnWidth(1, 250)

        # Navegação
        navegacao_layout = QHBoxLayout()
        self.btn_anterior_mei = QPushButton("Anterior")
        self.btn_proximo_mei = QPushButton("Próximo")
        self.btn_anterior_mei.clicked.connect(self.ir_para_anterior_mei)
        self.btn_proximo_mei.clicked.connect(self.ir_para_proximo_mei)
        navegacao_layout.addWidget(self.btn_anterior_mei)
        navegacao_layout.addWidget(self.btn_proximo_mei)
        layout.addLayout(navegacao_layout)

        self.setLayout(layout)
        self.carregar_dados()

    def carregar_dados(self):
        filtro = self.input_filtro.text().strip()
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()

        if filtro:
            cursor.execute(
                """
                SELECT rowid, nome, email, senha_gov, cnpj 
                FROM mei 
                WHERE nome LIKE ? OR cnpj LIKE ?
                ORDER BY nome
            """,
                (f"%{filtro}%", f"%{filtro}%"),
            )
        else:
            cursor.execute(
                "SELECT rowid, nome, email, senha_gov, cnpj FROM mei ORDER BY nome"
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
            rowid, nome, email, senha, cnpj = row

            # Formatar CNPJ
            cnpj_limpo = "".join(filter(str.isdigit, cnpj))
            if len(cnpj_limpo) == 14:
                cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
            else:
                cnpj_formatado = cnpj

            self.tabela.setItem(i, 0, QTableWidgetItem(nome))
            self.tabela.setItem(i, 1, QTableWidgetItem(email))
            self.tabela.setItem(i, 2, QTableWidgetItem(senha))
            self.tabela.setItem(i, 3, QTableWidgetItem(cnpj_formatado))

            # Botão Editar
            btn_editar = QPushButton("Editar")
            btn_editar.clicked.connect(
                lambda _, rid=rowid: self.abrir_dialogo_cadastro(editar_id=rid)
            )
            self.tabela.setCellWidget(i, 4, btn_editar)

            # Botão Excluir
            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda _, rid=rowid: self.excluir_mei(rid))
            self.tabela.setCellWidget(i, 5, btn_excluir)

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

        # Se edição, carregar dados existentes
        if editar_id:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nome, email, senha_gov, cnpj FROM mei WHERE rowid = ?",
                (editar_id,),
            )
            dados = cursor.fetchone()
            conn.close()
            if dados:
                input_nome.setText(dados[0])
                input_email.setText(dados[1])
                input_senha.setText(dados[2])
                input_cnpj.setText(dados[3])

        layout.addRow("Nome:", input_nome)
        layout.addRow("Email:", input_email)
        layout.addRow("Senha Gov:", input_senha)
        layout.addRow("CNPJ:", input_cnpj)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(
            lambda: self.salvar_mei(
                dialog, input_nome, input_email, input_senha, input_cnpj, editar_id
            )
        )
        layout.addRow(btn_salvar)

        dialog.setLayout(layout)
        dialog.exec_()

    def salvar_mei(self, dialog, nome, email, senha, cnpj, editar_id=None):
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        if editar_id:
            cursor.execute(
                "UPDATE mei SET nome = ?, email = ?, senha_gov = ?, cnpj = ? WHERE rowid = ?",
                (nome.text(), email.text(), senha.text(), cnpj.text(), editar_id),
            )
        else:
            cursor.execute(
                "INSERT INTO mei (nome, email, senha_gov, cnpj) VALUES (?, ?, ?, ?)",
                (nome.text(), email.text(), senha.text(), cnpj.text()),
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

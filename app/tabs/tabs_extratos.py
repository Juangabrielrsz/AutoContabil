from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QDialog,
)
from PyQt5.QtCore import Qt, QDate
import sqlite3
import os
import pandas as pd


class TabsExtratos(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🔍 Filtros
        self.filtro_layout = QHBoxLayout()
        self.layout.addLayout(self.filtro_layout)

        self.label_cliente = QLabel("Cliente:")
        self.combo_cliente = QComboBox()
        self.filtro_layout.addWidget(self.label_cliente)
        self.filtro_layout.addWidget(self.combo_cliente)

        self.label_data_inicio = QLabel("De:")
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))

        self.label_data_fim = QLabel("Até:")
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())

        self.filtro_layout.addWidget(self.label_data_inicio)
        self.filtro_layout.addWidget(self.data_inicio)
        self.filtro_layout.addWidget(self.label_data_fim)
        self.filtro_layout.addWidget(self.data_fim)

        self.botao_filtrar = QPushButton("Filtrar")
        self.botao_filtrar.clicked.connect(self.carregar_dados)
        self.botao_limpar = QPushButton("Limpar Filtros")
        self.botao_limpar.clicked.connect(self.limpar_filtros)

        self.filtro_layout.addWidget(self.botao_filtrar)
        self.filtro_layout.addWidget(self.botao_limpar)

        # ➕ Botão Novo Extrato
        self.botao_novo = QPushButton("Novo Extrato")
        self.botao_novo.clicked.connect(self.abrir_novo_extrato)
        self.layout.addWidget(self.botao_novo)

        # 📋 Tabela de extratos
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)
        self.tabela.cellDoubleClicked.connect(self.abrir_edicao_extrato)

        # Navegação de páginas
        self.layout_navegacao = QHBoxLayout()
        self.btn_anterior = QPushButton("⬅ Anterior")
        self.btn_proximo = QPushButton("Próxima ➡")

        self.btn_anterior.clicked.connect(self.pagina_anterior)
        self.btn_proximo.clicked.connect(self.pagina_proxima)

        self.layout_navegacao.addWidget(self.btn_anterior)
        self.layout_navegacao.addWidget(self.btn_proximo)
        self.layout.addLayout(self.layout_navegacao)

        # Rodapé
        self.rodape_layout = QHBoxLayout()
        self.label_entradas = QLabel("Entradas: R$ 0.00")
        self.label_saidas = QLabel("Saídas: R$ 0.00")
        self.label_saldo = QLabel("Saldo: R$ 0.00")
        self.rodape_layout.addWidget(self.label_entradas)
        self.rodape_layout.addWidget(self.label_saidas)
        self.rodape_layout.addWidget(self.label_saldo)
        self.layout.addLayout(self.rodape_layout)

        self.botao_exportar = QPushButton("Exportar para Excel")
        self.botao_exportar.clicked.connect(self.exportar_para_excel)
        self.layout.addWidget(self.botao_exportar)

        # Combobox para tipos de movimentação
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Entrada", "Saída"])
        self.filtro_layout.addWidget(QLabel("Tipo:"))
        self.filtro_layout.addWidget(self.combo_tipo)

        self.pagina_atual = 0
        self.registros_por_pagina = 20

        self.carregar_clientes()
        self.carregar_dados()
        self.layout_navegacao = QHBoxLayout()

    def carregar_clientes(self):
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cliente FROM extratos ORDER BY cliente")
        clientes = cursor.fetchall()
        conn.close()

        self.combo_cliente.clear()
        self.combo_cliente.addItem("Todos")
        for cliente in clientes:
            self.combo_cliente.addItem(cliente[0])

    def carregar_dados(self):
        caminho_banco = os.path.join(
            os.path.dirname(__file__), "..", "app", "banco_dados.db"
        )
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()

        tipo = self.combo_tipo.currentText()
        data_ini = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        query_base = """
            SELECT id, cliente, descricao, data, tipo, valor 
            FROM extratos 
            WHERE data BETWEEN ? AND ?
        """
        params = [data_ini, data_fim]

        if tipo != "Todos":
            query_base += " AND tipo = ?"
            params.append(tipo)

        cursor.execute(query_base, params)
        todos_dados = cursor.fetchall()

        # Paginação
        total_registros = len(todos_dados)
        self.total_paginas = (
            total_registros + self.registros_por_pagina - 1
        ) // self.registros_por_pagina

        inicio = self.pagina_atual * self.registros_por_pagina
        fim = inicio + self.registros_por_pagina
        dados = todos_dados[inicio:fim]

        #   Preenchendo a tabela
        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Cliente", "Descrição", "Data", "Tipo", "Valor"]
        )

        total_entradas = 0.0
        total_saidas = 0.0

        for i, row in enumerate(dados):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if j == 5:  # Coluna Valor
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabela.setItem(i, j, item)

        if row[4] == "Entrada":
            total_entradas += float(row[5])
        elif row[4] == "Saída":
            total_saidas += float(row[5])

        # Totais e saldo
        self.label_entradas.setText(f"Entradas: R$ {total_entradas:,.2f}")
        self.label_saidas.setText(f"Saídas: R$ {total_saidas:,.2f}")
        self.label_saldo.setText(f"Saldo: R$ {total_entradas - total_saidas:,.2f}")

        self.tabela.resizeColumnsToContents()
        self.tabela.setSortingEnabled(True)

        # Controle de navegação
        self.btn_anterior.setEnabled(self.pagina_atual > 0)
        self.btn_proximo.setEnabled(self.pagina_atual < self.total_paginas - 1)

        conn.close()

    def filtrar_dados(self):
        self.pagina_atual = 0
        self.carregar_dados()

    def pagina_anterior(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self.carregar_dados()

    def pagina_proxima(self):
        if self.pagina_atual < self.total_paginas - 1:
            self.pagina_atual += 1
            self.carregar_dados()

    def abrir_novo_extrato(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Extrato")
        layout = QVBoxLayout()

        input_cliente = QLineEdit()
        input_descricao = QLineEdit()
        input_data = QDateEdit()
        input_data.setCalendarPopup(True)
        input_data.setDate(QDate.currentDate())

        combo_tipo = QComboBox()
        combo_tipo.addItems(["Entrada", "Saída"])

        input_valor = QLineEdit()

        layout.addWidget(QLabel("Cliente"))
        layout.addWidget(input_cliente)
        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(input_descricao)
        layout.addWidget(QLabel("Data"))
        layout.addWidget(input_data)
        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(combo_tipo)
        layout.addWidget(QLabel("Valor"))
        layout.addWidget(input_valor)

        botoes = QHBoxLayout()
        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")
        botoes.addWidget(btn_salvar)
        botoes.addWidget(btn_cancelar)
        layout.addLayout(botoes)

        dialog.setLayout(layout)

        def salvar():
            try:
                conn = sqlite3.connect("app/database.db")
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO extratos (cliente, descricao, data, tipo, valor)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        input_cliente.text(),
                        input_descricao.text(),
                        input_data.date().toString("yyyy-MM-dd"),
                        combo_tipo.currentText(),
                        float(input_valor.text().replace(",", ".")),
                    ),
                )
                conn.commit()
                conn.close()
                self.carregar_dados()
                self.carregar_clientes()
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar: {str(e)}")

        btn_salvar.clicked.connect(salvar)
        btn_cancelar.clicked.connect(dialog.reject)

        dialog.exec_()

    def exportar_para_excel(self):
        cliente_filtro = self.combo_cliente.currentText()
        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("app/database.db")

        if cliente_filtro == "Todos":
            query = "SELECT * FROM extratos WHERE data BETWEEN ? AND ?"
            params = (data_inicio, data_fim)
        else:
            query = "SELECT * FROM extratos WHERE cliente = ? AND data BETWEEN ? AND ?"
            params = (cliente_filtro, data_inicio, data_fim)

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if df.empty:
            QMessageBox.information(self, "Aviso", "Nenhum dado para exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo", "", "Excel Files (*.xlsx)"
        )
        if path:
            if not path.endswith(".xlsx"):
                path += ".xlsx"
            try:
                df.to_excel(path, index=False)
                QMessageBox.information(
                    self, "Sucesso", f"Extratos exportados com sucesso para:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")

    def limpar_filtros(self):
        self.combo_cliente.setCurrentIndex(0)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.data_fim.setDate(QDate.currentDate())
        self.carregar_dados()

    def abrir_edicao_extrato(self, row, column):
        id_extrato = self.tabela.item(row, 0).text()
        cliente = self.tabela.item(row, 1).text()
        descricao = self.tabela.item(row, 2).text()
        data = self.tabela.item(row, 3).text()
        tipo = self.tabela.item(row, 4).text()
        valor = self.tabela.item(row, 5).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar/Excluir Extrato")
        layout = QVBoxLayout()

        input_cliente = QLineEdit(cliente)
        input_descricao = QLineEdit(descricao)
        input_data = QDateEdit()
        input_data.setCalendarPopup(True)
        input_data.setDate(QDate.fromString(data, "yyyy-MM-dd"))

        combo_tipo = QComboBox()
        combo_tipo.addItems(["Entrada", "Saída"])
        combo_tipo.setCurrentText(tipo)

        input_valor = QLineEdit(valor)

        layout.addWidget(QLabel("Cliente"))
        layout.addWidget(input_cliente)
        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(input_descricao)
        layout.addWidget(QLabel("Data"))
        layout.addWidget(input_data)
        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(combo_tipo)
        layout.addWidget(QLabel("Valor"))
        layout.addWidget(input_valor)

        botoes = QHBoxLayout()
        btn_salvar = QPushButton("Salvar")
        btn_excluir = QPushButton("Excluir")
        btn_cancelar = QPushButton("Cancelar")
        botoes.addWidget(btn_salvar)
        botoes.addWidget(btn_excluir)
        botoes.addWidget(btn_cancelar)
        layout.addLayout(botoes)

        dialog.setLayout(layout)

        def salvar():
            try:
                valor_float = float(input_valor.text().replace(",", "."))
                conn = sqlite3.connect("app/database.db")
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE extratos
                    SET cliente = ?, descricao = ?, data = ?, tipo = ?, valor = ?
                    WHERE id = ?
                    """,
                    (
                        input_cliente.text(),
                        input_descricao.text(),
                        input_data.date().toString("yyyy-MM-dd"),
                        combo_tipo.currentText(),
                        valor_float,
                        id_extrato,
                    ),
                )
                conn.commit()
                conn.close()
                self.carregar_dados()
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar: {str(e)}")

        def excluir():
            confirm = QMessageBox.question(
                self,
                "Confirmação",
                "Tem certeza que deseja excluir este extrato?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                conn = sqlite3.connect("app/database.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM extratos WHERE id = ?", (id_extrato,))
                conn.commit()
                conn.close()
                self.carregar_dados()
                dialog.accept()

        btn_salvar.clicked.connect(salvar)
        btn_excluir.clicked.connect(excluir)
        btn_cancelar.clicked.connect(dialog.reject)

        dialog.exec_()

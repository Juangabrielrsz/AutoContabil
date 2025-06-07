from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
import os
import xml.etree.ElementTree as ET
import sqlite3
import openpyxl

class TabsNotasFiscais(QWidget):
    def __init__(self):
        super().__init__()
        self.arquivos = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Filtros de busca
        filtro_layout = QHBoxLayout()
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("Buscar por CNPJ")
        self.input_mes = QLineEdit()
        self.input_mes.setPlaceholderText("Buscar por Mês (YYYY-MM)")
        self.input_emitente = QLineEdit()
        self.input_emitente.setPlaceholderText("Buscar por Emitente")
        self.botao_buscar = QPushButton("Buscar")
        self.botao_buscar.clicked.connect(self.buscar_notas)

        filtro_layout.addWidget(self.input_cnpj)
        filtro_layout.addWidget(self.input_mes)
        filtro_layout.addWidget(self.input_emitente)
        filtro_layout.addWidget(self.botao_buscar)

        layout.addLayout(filtro_layout)

        # Botões principais
        self.botao_carregar = QPushButton("Carregar NFes (XML)")
        self.botao_carregar.clicked.connect(self.carregar_arquivos)

        self.botao_processar = QPushButton("Processar e Salvar NFes")
        self.botao_processar.clicked.connect(self.processar_xmls)

        self.botao_exportar = QPushButton("Exportar para Excel")
        self.botao_exportar.clicked.connect(self.exportar_para_excel)

        layout.addWidget(self.botao_carregar)
        layout.addWidget(self.botao_processar)
        layout.addWidget(self.botao_exportar)

        self.tabela_resultado = QTableWidget()
        self.tabela_resultado.setColumnCount(6)
        self.tabela_resultado.setHorizontalHeaderLabels([
            "Arquivo", "Emitente", "CNPJ", "Número", "Data de Emissão", "Valor Total"
        ])
        self.tabela_resultado.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabela_resultado)

        self.setLayout(layout)

    def carregar_arquivos(self):
        arquivos, _ = QFileDialog.getOpenFileNames(self, "Selecionar NFes", "", "Arquivos XML (*.xml)")
        if arquivos:
            self.arquivos = arquivos
            QMessageBox.information(self, "Arquivos Selecionados", f"{len(arquivos)} arquivos selecionados.")

    def processar_xmls(self):
        if not self.arquivos:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo carregado.")
            return

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()

        for caminho in self.arquivos:
            try:
                tree = ET.parse(caminho)
                root = tree.getroot()
                ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

                emit = root.find('.//nfe:emit', ns)
                nome_emitente = emit.find('nfe:xNome', ns).text
                cnpj_emitente = emit.find('nfe:CNPJ', ns).text

                ide = root.find('.//nfe:ide', ns)
                numero_nota = ide.find('nfe:nNF', ns).text
                data_emissao = ide.find('nfe:dhEmi', ns)
                data_emissao = data_emissao.text if data_emissao is not None else "N/D"

                total = root.find('.//nfe:ICMSTot', ns)
                valor_total = float(total.find('nfe:vNF', ns).text)

                cursor.execute('''
                    INSERT INTO notas_fiscais (arquivo, emitente, cnpj, numero, data_emissao, valor_total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    os.path.basename(caminho),
                    nome_emitente,
                    cnpj_emitente,
                    numero_nota,
                    data_emissao,
                    valor_total
                ))

            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao processar {os.path.basename(caminho)}: {e}")

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Sucesso", "Notas processadas e salvas com sucesso!")
        self.buscar_notas()  # atualiza a tabela após salvar

    def exportar_para_excel(self):
        try:
            conn = sqlite3.connect("app/database.db")
            cursor = conn.cursor()

            cursor.execute("SELECT arquivo, emitente, cnpj, numero, data_emissao, valor_total FROM notas_fiscais")
            dados = cursor.fetchall()
            conn.close()

            if not dados:
                QMessageBox.information(self, "Aviso", "Nenhuma nota fiscal encontrada para exportar.")
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Notas Fiscais"

            colunas = ["Arquivo", "Emitente", "CNPJ", "Número", "Data de Emissão", "Valor Total"]
            ws.append(colunas)

            for linha in dados:
                ws.append(linha)

            caminho_excel = os.path.join(os.getcwd(), "notas_fiscais_exportadas.xlsx")
            wb.save(caminho_excel)

            QMessageBox.information(self, "Sucesso", f"Exportado para {caminho_excel}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")

    def buscar_notas(self):
        cnpj = self.input_cnpj.text().strip()
        mes = self.input_mes.text().strip()
        emitente = self.input_emitente.text().strip()

        query = "SELECT arquivo, emitente, cnpj, numero, data_emissao, valor_total FROM notas_fiscais WHERE 1=1"
        params = []

        if cnpj:
            query += " AND cnpj LIKE ?"
            params.append(f"%{cnpj}%")
        if mes:
            query += " AND substr(data_emissao, 1, 7) = ?"
            params.append(mes)
        if emitente:
            query += " AND emitente LIKE ?"
            params.append(f"%{emitente}%")

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()

        self.tabela_resultado.setRowCount(0)

        if resultados:
            self.tabela_resultado.setRowCount(len(resultados))
            for row_idx, row_data in enumerate(resultados):
                for col_idx, valor in enumerate(row_data):
                    item = QTableWidgetItem(str(valor))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.tabela_resultado.setItem(row_idx, col_idx, item)
        else:
            QMessageBox.information(self, "Resultado", "Nenhuma nota encontrada com os filtros informados.")

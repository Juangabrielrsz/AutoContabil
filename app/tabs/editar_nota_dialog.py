from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)
import sqlite3
from app.utils import get_writable_db_path


class EditarNotaDialog(QDialog):
    def __init__(self, nota_id, dados, parent=None):
        super().__init__(parent)
        self.nota_id = nota_id
        self.setWindowTitle("Editar Nota Fiscal")
        self.setFixedWidth(400)

        self.emitente = QLineEdit(dados["emitente"])
        self.cnpj = QLineEdit(dados["cnpj"])
        self.numero = QLineEdit(dados["numero"])
        self.data_emissao = QLineEdit(dados["data_emissao"])
        self.valor_total = QLineEdit(str(dados["valor_total"]))

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Emitente:"))
        layout.addWidget(self.emitente)
        layout.addWidget(QLabel("CNPJ:"))
        layout.addWidget(self.cnpj)
        layout.addWidget(QLabel("Número:"))
        layout.addWidget(self.numero)
        layout.addWidget(QLabel("Data de Emissão (YYYY-MM-DD):"))
        layout.addWidget(self.data_emissao)
        layout.addWidget(QLabel("Valor Total:"))
        layout.addWidget(self.valor_total)

        botoes = QHBoxLayout()
        salvar_btn = QPushButton("Salvar")
        salvar_btn.clicked.connect(self.salvar_edicao)
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        botoes.addWidget(salvar_btn)
        botoes.addWidget(cancelar_btn)

        layout.addLayout(botoes)
        self.setLayout(layout)

    def salvar_edicao(self):
        try:

            conn = sqlite3.connect(get_writable_db_path())
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE notas_fiscais SET emitente = ?, cnpj = ?, numero = ?, data_emissao = ?, valor_total = ?
                WHERE id = ?
            """,
                (
                    self.emitente.text(),
                    self.cnpj.text(),
                    self.numero.text(),
                    self.data_emissao.text(),
                    float(self.valor_total.text()),
                    self.nota_id,
                ),
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sucesso", "Nota atualizada com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

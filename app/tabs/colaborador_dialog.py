from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QDoubleSpinBox,
    QPushButton,
)
from PyQt5.QtCore import QDate
import sqlite3


class ColaboradorDialog(QDialog):
    def __init__(self, parent=None, colaborador=None):
        super().__init__(parent)
        self.colaborador = colaborador
        self.setWindowTitle("Editar Colaborador" if colaborador else "Novo Colaborador")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_cpf = QLineEdit()
        self.input_cnpj = QLineEdit()
        self.input_empresa = QLineEdit()
        self.input_escritorio = QLineEdit()
        self.input_cargo = QLineEdit()
        self.input_salario = QDoubleSpinBox()
        self.input_salario.setMaximum(999999.99)
        self.input_contrato = QComboBox()
        self.input_contrato.addItems(["CLT", "PJ", "Estágio", "Outros"])
        self.input_admissao = QDateEdit()
        self.input_admissao.setCalendarPopup(True)
        self.input_demissao = QDateEdit()
        self.input_demissao.setCalendarPopup(True)
        self.input_demissao.setDate(QDate(2000, 1, 1))
        self.input_obs = QTextEdit()

        layout.addRow("Nome:", self.input_nome)
        layout.addRow("CPF:", self.input_cpf)
        layout.addRow("CNPJ Empresa:", self.input_cnpj)
        layout.addRow("Empresa:", self.input_empresa)
        layout.addRow("Escritório:", self.input_escritorio)
        layout.addRow("Cargo:", self.input_cargo)
        layout.addRow("Salário:", self.input_salario)
        layout.addRow("Tipo de Contrato:", self.input_contrato)
        layout.addRow("Admissão:", self.input_admissao)
        layout.addRow("Demissão:", self.input_demissao)
        layout.addRow("Observações:", self.input_obs)

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar)
        layout.addRow(self.btn_salvar)

        self.setLayout(layout)

        if self.colaborador:
            self.preencher_dados()

    def preencher_dados(self):
        c = self.colaborador
        self.input_nome.setText(c[1])
        self.input_cpf.setText(c[2])
        self.input_cnpj.setText(c[3])
        self.input_empresa.setText(c[4])
        self.input_escritorio.setText(c[5])
        self.input_cargo.setText(c[6])
        self.input_salario.setValue(c[7])
        self.input_contrato.setCurrentText(c[8])
        self.input_admissao.setDate(QDate.fromString(c[9], "yyyy-MM-dd"))
        self.input_demissao.setDate(
            QDate.fromString(c[10], "yyyy-MM-dd") if c[10] else QDate(2000, 1, 1)
        )
        self.input_obs.setText(c[11])

    def salvar(self):
        dados = (
            self.input_nome.text(),
            self.input_cpf.text(),
            self.input_cnpj.text(),
            self.input_empresa.text(),
            self.input_escritorio.text(),
            self.input_cargo.text(),
            float(self.input_salario.value()),
            self.input_contrato.currentText(),
            self.input_admissao.date().toString("yyyy-MM-dd"),
            self.input_demissao.date().toString("yyyy-MM-dd"),
            self.input_obs.toPlainText(),
        )

        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()

        if self.colaborador:
            cursor.execute(
                """
                UPDATE colaboradores
                SET nome=?, cpf=?, cnpj_empresa=?, empresa=?, escritorio=?, cargo=?, salario=?,
                    tipo_contrato=?, data_admissao=?, data_demissao=?, observacoes=?
                WHERE id=?
            """,
                dados + (self.colaborador[0],),
            )
        else:
            cursor.execute(
                """
                INSERT INTO colaboradores
                (nome, cpf, cnpj_empresa, empresa, escritorio, cargo, salario,
                 tipo_contrato, data_admissao, data_demissao, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                dados,
            )

        conn.commit()
        conn.close()
        self.accept()

from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QDoubleSpinBox,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import QDate, QLocale, Qt
import sqlite3
from PyQt5.QtWidgets import QCheckBox
from app.utils import get_writable_db_path


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
        self.input_cpf.setInputMask("000.000.000-00;_")
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setInputMask("00.000.000/0000-00;_")
        self.input_empresa = QLineEdit()
        self.input_escritorio = QLineEdit()
        self.input_cargo = QLineEdit()
        self.input_salario = QDoubleSpinBox()
        self.input_salario.setMaximum(999999.99)
        self.input_salario.setDecimals(2)
        self.input_salario.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.input_salario.setPrefix("R$ ")
        self.input_contrato = QComboBox()
        self.input_contrato.addItems(["CLT", "PJ", "Estágio", "Outros"])
        self.input_admissao = QDateEdit()
        self.input_admissao.setCalendarPopup(True)
        self.input_admissao.dateChanged.connect(self.validar_datas)

        self.input_data_demissao = QDateEdit()
        self.input_data_demissao.setCalendarPopup(True)
        self.input_data_demissao.setDate(QDate.currentDate())

        self.checkbox_ativo = QCheckBox("Ainda está na empresa")
        self.checkbox_ativo.setChecked(True)  # Default como ativo
        self.checkbox_ativo.stateChanged.connect(self.toggle_demissao)
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
        layout.addRow("Data de Demissão:", self.input_data_demissao)
        layout.addRow("", self.checkbox_ativo)
        layout.addRow("Observações:", self.input_obs)

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar)
        layout.addRow(self.btn_salvar)

        self.setLayout(layout)

        if self.colaborador:
            self.preencher_dados()

    def toggle_demissao(self, state):
        if state == Qt.Checked:
            self.input_data_demissao.setEnabled(False)
        else:
            self.input_data_demissao.setEnabled(True)

    def validar_datas(self):
        data_admissao = self.input_admissao.date()
        data_demissao = self.input_data_demissao.date()

        if data_demissao < data_admissao:
            QMessageBox.warning(
                self,
                "Data inválida",
                "A data de demissão não pode ser anterior à data de admissão.",
            )
            self.input_data_demissao.setDate(data_admissao)

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
        self.input_data_demissao.setDate(
            QDate.fromString(c[10], "yyyy-MM-dd") if c[10] else QDate(2000, 1, 1)
        )
        self.input_obs.setText(c[11])

    def salvar(self):
        data_demissao = (
            ""
            if self.checkbox_ativo.isChecked()
            else self.input_data_demissao.date().toString("yyyy-MM-dd")
        )

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
            data_demissao,
            self.input_obs.toPlainText(),
        )

        conn = sqlite3.connect(get_writable_db_path())
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
        if self.input_data_demissao.date() < self.input_admissao.date():
            QMessageBox.warning(
                self, "Erro", "Data de demissão não pode ser anterior à de admissão."
            )
            return

        conn.commit()
        conn.close()
        self.accept()

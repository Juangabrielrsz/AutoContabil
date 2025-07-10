from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyQt5.QtWidgets import QFileDialog
import fitz  # PyMuPDF
import os


def gerar_pdf_holerite(self, folha):
    # 1. Escolher onde salvar o PDF
    nome_arquivo_sugerido = f"holerite_{folha['nome'].replace(' ', '_')}_07-2025.pdf"
    caminho_saida, _ = QFileDialog.getSaveFileName(
        self, "Salvar Holerite", nome_arquivo_sugerido, "PDF Files (*.pdf)"
    )
    if not caminho_saida:
        return  # Cancelado

    # 2. Caminho do modelo de fundo
    MODELO_PDF = os.path.join(
        os.path.dirname(__file__), "modelos", "holerite_modelo_em_branco.pdf"
    )
    temp_pdf_path = "temp_overlay.pdf"

    # 3. Criar o overlay com os dados
    c = canvas.Canvas(temp_pdf_path, pagesize=A4)

    def mm_to_pt(x_mm, y_mm):
        x = x_mm * mm
        y = A4[1] - y_mm * mm
        return x, y

    # Título
    c.setFont("Helvetica-Bold", 12)
    c.drawString(*mm_to_pt(70, 10), "RECIBO DE PAGAMENTO DE SALÁRIO")

    # Nome da empresa no topo
    c.setFont("Helvetica-Bold", 10)
    c.drawString(*mm_to_pt(23, 18), folha["empresa"])

    # Nome do funcionário e cargo
    c.setFont("Helvetica-Bold", 9)
    c.drawString(*mm_to_pt(23, 40), folha["nome"])
    c.setFont("Helvetica", 9)
    c.drawString(*mm_to_pt(100, 40), "CBO: 422110")
    c.drawString(*mm_to_pt(100, 45), f"Admissão: {folha['data_admissao']}")
    c.drawString(*mm_to_pt(140, 45), "Departamento: PESSOAL")
    c.drawString(*mm_to_pt(140, 50), f"Cargo: {folha['cargo']}")

    # Rubricas (com valores padrão corretos)
    rubricas = [
        ("8781", "SALÁRIO", "30", folha["salario_base"], ""),
        ("995", "SALÁRIO FAMÍLIA", "1", folha["beneficios"], ""),
        ("998", "INSS", "", "", 100.00),
        ("993", "DESCONTO", "", "", folha["descontos"]),
        ("048", "VALE TRANSPORTE", "6", "", 80.00),
    ]

    # Cabeçalho da tabela
    c.setFont("Helvetica-Bold", 8)
    x_rub = [22, 42, 95, 130, 165]  # mm
    y_start = 75
    c.drawString(*mm_to_pt(x_rub[0], y_start), "Código")
    c.drawString(*mm_to_pt(x_rub[1], y_start), "Descrição")
    c.drawString(*mm_to_pt(x_rub[2], y_start), "Referência")
    c.drawString(*mm_to_pt(x_rub[3], y_start), "Vencimentos")
    c.drawString(*mm_to_pt(x_rub[4], y_start), "Descontos")

    # Linhas da tabela
    c.setFont("Helvetica", 8)
    y_line = y_start + 7
    for cod, desc, ref, venc, descs in rubricas:
        y_line += 6
        c.drawString(*mm_to_pt(x_rub[0], y_line), str(cod))
        c.drawString(*mm_to_pt(x_rub[1], y_line), str(desc))
        c.drawString(*mm_to_pt(x_rub[2], y_line), str(ref))
        if venc:
            c.drawRightString(
                mm_to_pt(x_rub[3] + 25, y_line)[0],
                mm_to_pt(0, y_line)[1],
                f"R$ {float(venc):,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )
        if descs:
            c.drawRightString(
                mm_to_pt(x_rub[4] + 25, y_line)[0],
                mm_to_pt(0, y_line)[1],
                f"R$ {float(descs):,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )

    # Totais
    total_venc = folha["salario_base"] + folha["beneficios"]
    total_desc = folha["descontos"] + 100 + 80
    salario_liquido = total_venc - total_desc

    c.setFont("Helvetica-Bold", 8)
    y_tot = y_line + 10
    c.drawString(*mm_to_pt(130, y_tot), "Total Vencimentos:")
    c.drawRightString(
        *mm_to_pt(190, y_tot),
        f"R$ {total_venc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    )
    y_tot += 5
    c.drawString(*mm_to_pt(130, y_tot), "Total Descontos:")
    c.drawRightString(
        *mm_to_pt(190, y_tot),
        f"R$ {total_desc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    )
    y_tot += 7
    c.drawString(*mm_to_pt(130, y_tot), "Salário Líquido:")
    c.drawRightString(
        *mm_to_pt(190, y_tot),
        f"R$ {salario_liquido:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
    )

    c.save()

    # 4. Combinar com modelo
    modelo = fitz.open(MODELO_PDF)
    overlay = fitz.open(temp_pdf_path)
    modelo[0].show_pdf_page(modelo[0].rect, overlay, 0)
    modelo.save(caminho_saida)
    modelo.close()
    overlay.close()

    # Limpar temporário
    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)

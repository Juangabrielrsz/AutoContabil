from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


def gerar_pdf_holerite_detalhado(
    colaborador, data_pagamento, beneficios, descontos, salario_liquido
):
    nome_arquivo = f"holerite_{colaborador[1].replace(' ', '_')}_{data_pagamento}.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    y = altura - 20 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "EMPRESA EXEMPLO LTDA - ME")
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, y - 5 * mm, "CNPJ: 00.000.000/0001-00")
    c.drawString(100 * mm, y - 5 * mm, "CC: GERAL")
    c.drawString(100 * mm, y - 10 * mm, "Mensalista")
    c.drawString(160 * mm, y - 10 * mm, f"Folha Mensal")
    c.drawString(160 * mm, y - 15 * mm, f"{data_pagamento[-7:]}")

    # Dados do funcionário
    y -= 25 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, f"{colaborador[1]}")
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, y - 5 * mm, f"{colaborador[4]}")
    c.drawString(100 * mm, y, "CBO: 422110")
    c.drawString(100 * mm, y - 5 * mm, "Departamento: 1")
    c.drawString(140 * mm, y - 5 * mm, "Filial: 1")
    c.drawString(100 * mm, y - 10 * mm, f"Admissão: {colaborador[7]}")

    # Tabela de proventos e descontos
    y -= 20 * mm
    c.setFont("Helvetica-Bold", 8)
    c.drawString(22 * mm, y, "Código")
    c.drawString(40 * mm, y, "Descrição")
    c.drawString(100 * mm, y, "Referência")
    c.drawString(120 * mm, y, "Vencimentos")
    c.drawString(150 * mm, y, "Descontos")

    rubricas = [
        ("8781", "SALARIO", "30,00", f"{colaborador[5]:,.2f}", ""),
        ("995", "SALARIO FAMILIA", "31,71", f"{beneficios:,.2f}", ""),
        ("998", "I.N.S.S.", "8,00", "", "87,56"),
        ("993", "ARRED. MES ANTERIOR", "0,54", "", f"{descontos:,.2f}"),
        ("048", "VALE TRANSPORTE", "6,00", "", "65,67"),
    ]

    c.setFont("Helvetica", 8)
    y -= 8 * mm
    for cod, desc, ref, venc, descs in rubricas:
        c.drawString(22 * mm, y, cod)
        c.drawString(40 * mm, y, desc)
        c.drawString(100 * mm, y, ref)
        if venc:
            c.drawRightString(145 * mm, y, venc)
        if descs:
            c.drawRightString(180 * mm, y, descs)
        y -= 6 * mm

    # Totais
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 8)
    c.drawString(100 * mm, y, "Total de Vencimentos:")
    c.drawRightString(145 * mm, y, f"{colaborador[5] + beneficios:,.2f}")
    c.drawString(100 * mm, y - 5 * mm, "Total de Descontos:")
    c.drawRightString(180 * mm, y - 5 * mm, f"{descontos + 87.56 + 65.67:,.2f}")

    y -= 15 * mm
    c.drawString(100 * mm, y, "Valor Líquido:")
    c.drawRightString(180 * mm, y, f"{salario_liquido:,.2f}")

    # Rodapé com bases
    y -= 20 * mm
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, y, f"Salário Base: {colaborador[5]:,.2f}")
    c.drawString(60 * mm, y, f"Base INSS: {colaborador[5]:,.2f}")
    c.drawString(100 * mm, y, f"Base FGTS: {colaborador[5]:,.2f}")
    c.drawString(140 * mm, y, f"FGTS do mês: 87,56")

    y -= 6 * mm
    c.drawString(20 * mm, y, f"Base IRRF: 817,35")
    c.drawString(60 * mm, y, f"IRRF: 0,00")

    # Assinatura
    y -= 20 * mm
    c.drawString(20 * mm, y, "Assinatura do Funcionário: ____________________________")
    c.drawRightString(190 * mm, y, f"Data: ____/____/______")

    c.save()

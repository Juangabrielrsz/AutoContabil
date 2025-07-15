from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyQt5.QtWidgets import QFileDialog
import fitz  # PyMuPDF
import os
from reportlab.pdfgen import canvas


def mm_to_pt(x_mm, y_mm):
    x = x_mm * mm
    y = A4[1] - y_mm * mm
    return x, y


def gerar_pdf_holerite(self, folha):
    MODELO_PDF = "app/tabs/modelos/holerite_modelo_em_branco.pdf"
    temp_overlay_path = "overlay_temp.pdf"

    nome_arquivo_sugerido = (
        f"holerite_{folha['nome'].replace(' ', '_')}_{folha['data_pagamento']}.pdf"
    )
    caminho_saida, _ = QFileDialog.getSaveFileName(
        self, "Salvar Holerite", nome_arquivo_sugerido, "PDF Files (*.pdf)"
    )
    if not caminho_saida:
        return

    c = canvas.Canvas(temp_overlay_path, pagesize=A4)

    def desenhar_holerite(offset_y):
        c.setFont("Times-Roman", 11)
        c.drawString(*mm_to_pt(4, 5 + offset_y), folha["empresa"])
        c.drawString(*mm_to_pt(4, 9 + offset_y), "CNPJ: 00.000.000/0001-00")
        c.drawString(*mm_to_pt(70, 8 + offset_y), "CC: GERAL")
        c.drawString(*mm_to_pt(73, 12 + offset_y), "Mensalista")
        c.drawString(*mm_to_pt(150, 8 + offset_y), "Folha Mensal")

        mes, ano = (
            folha["data_pagamento"].split("-")[1],
            folha["data_pagamento"].split("-")[0],
        )
        meses_pt = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }
        c.drawString(*mm_to_pt(150, 12 + offset_y), f"{meses_pt[mes]} de {ano}")

        c.drawString(*mm_to_pt(10, 19 + offset_y), folha["nome"])
        c.drawString(*mm_to_pt(10, 23 + offset_y), folha["cargo"])
        c.drawString(*mm_to_pt(125, 17 + offset_y), "422110")
        c.drawString(*mm_to_pt(125, 21 + offset_y), "Admissão:")
        c.drawString(*mm_to_pt(150, 21 + offset_y), folha["data_admissao"])

        # BASES de Cálculo
        salario_base = folha["salario_base"]
        base_inss = salario_base
        fgts_base = salario_base
        fgts_mes = round(fgts_base * 0.08, 2)

        # INSS
        if base_inss <= 1518.00:
            inss_aliq = 0.075
            inss_ded = 0
        elif base_inss <= 2793.88:
            inss_aliq = 0.09
            inss_ded = 22.77
        elif base_inss <= 4190.83:
            inss_aliq = 0.12
            inss_ded = 106.59
        else:
            inss_aliq = 0.14
            inss_ded = 190.40
        inss_valor = round(base_inss * inss_aliq - inss_ded, 2)

        # IRRF
        base_irrf = salario_base - inss_valor
        if base_irrf <= 2428.80:
            irrf_aliq = 0.0
            irrf_ded = 0.0
        elif base_irrf <= 2826.65:
            irrf_aliq = 0.075
            irrf_ded = 182.16
        elif base_irrf <= 3751.05:
            irrf_aliq = 0.15
            irrf_ded = 384.16
        elif base_irrf <= 4664.68:
            irrf_aliq = 0.225
            irrf_ded = 675.49
        else:
            irrf_aliq = 0.275
            irrf_ded = 908.73
        irrf_valor = max(round(base_irrf * irrf_aliq - irrf_ded, 2), 0)

        rubricas = []

        # Salário base
        rubricas.append(
            ("8781", "SALÁRIO", folha["dias_trabalhados"], folha["salario_base"], "")
        )

        # Benefícios
        if folha.get("beneficios", 0) > 0:
            rubricas.append(("995", "BENEFÍCIOS", "1", folha["beneficios"], ""))

        # Vale-refeição
        if folha.get("vale_refeicao", 0) > 0:
            rubricas.append(
                ("047", "VAL.REFEIÇÃO/ALIM.", "", folha["vale_refeicao"], "")
            )

        # Vale-transporte
        if folha.get("vale_transporte", 0) > 0:
            rubricas.append(
                ("048", "VALE TRANSPORTE", "", folha["vale_transporte"], "")
            )

        # Descontos
        if folha.get("outros_descontos", 0) > 0:
            rubricas.append(("049", "Descontos", "", "", folha["outros_descontos"]))

        # FGTS
        if inss_valor > 0:
            rubricas.append(("998", "I.N.S.S.", "", "", inss_valor))

        # I.R.R.F.
        if irrf_valor > 0:
            rubricas.append(("999", "I.R.R.F.", "", "", irrf_valor))

        # Preencher com linhas em branco até ter 6 linhas
        while len(rubricas) < 6:
            rubricas.append(("", "", "", "", ""))

        c.setFont("Courier", 10)
        y_base = 35 + offset_y
        for i, (cod, desc, ref, venc, descs) in enumerate(rubricas):
            y = y_base + i * 5
            c.drawString(*mm_to_pt(3, y), cod)
            c.drawString(*mm_to_pt(19, y), desc)
            if ref:
                c.drawRightString(*mm_to_pt(115, y), str(ref))
            if venc:
                c.drawRightString(
                    *mm_to_pt(140, y),
                    f"{venc:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )
            if descs:
                c.drawRightString(
                    *mm_to_pt(170, y),
                    f"{descs:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )

        # Totais
        total_venc = (
            folha["salario_base"]
            + folha.get("beneficios", 0)
            + folha.get("vale_refeicao", 0)
            + folha.get("vale_transporte", 0)
        )
        total_desc = folha.get("outros_descontos", 0) + inss_valor + irrf_valor
        liquido = total_venc - total_desc

        y_totais = 70 + offset_y
        c.setFont("Courier", 10)
        c.drawRightString(
            *mm_to_pt(140, y_totais + 30),
            f"{total_venc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawRightString(
            *mm_to_pt(168, y_totais + 30),
            f"{total_desc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawRightString(
            *mm_to_pt(168, y_totais + 40),
            f"{liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawString(*mm_to_pt(140, y_totais + 40), "➡")
        c.setFont("Times-Roman", 11)
        c.drawString(*mm_to_pt(3, y_totais + 35), folha["escritorio"])

        # Rodapé fixo
        c.setFont("Courier", 9)
        y_calc = 120 + offset_y
        c.drawString(
            *mm_to_pt(10, y_calc),
            f"{salario_base:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        )
        c.drawString(
            *mm_to_pt(35, y_calc),
            f"{base_inss:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawString(
            *mm_to_pt(62, y_calc),
            f"{fgts_base:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawString(
            *mm_to_pt(100, y_calc),
            f"{fgts_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawString(
            *mm_to_pt(125, y_calc),
            f"{base_irrf:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawString(*mm_to_pt(158, y_calc), f"{int(irrf_aliq*100)}%")

    desenhar_holerite(offset_y=0)
    desenhar_holerite(offset_y=140)

    c.save()
    modelo = fitz.open(MODELO_PDF)
    overlay = fitz.open(temp_overlay_path)
    modelo[0].show_pdf_page(modelo[0].rect, overlay, 0)
    modelo.save(caminho_saida)
    modelo.close()
    overlay.close()
    if os.path.exists(temp_overlay_path):
        os.remove(temp_overlay_path)

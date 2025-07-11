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
        # Corpo do texto
        c.setFont("Times-Roman", 11)

        # Cabeçalho: Empresa e CNPJ
        c.drawString(*mm_to_pt(4, 5 + offset_y), folha["empresa"])
        c.drawString(*mm_to_pt(4, 9 + offset_y), "CNPJ: 00.000.000/0001-00")

        # Linha: CC, tipo, folha, mês/ano
        c.drawString(*mm_to_pt(70, 8 + offset_y), "CC: GERAL")
        c.drawString(*mm_to_pt(73, 12 + offset_y), "Mensalista")
        c.drawString(*mm_to_pt(153, 8 + offset_y), "Folha Mensal")
        mes_ano = folha["data_pagamento"][:7].split("-")
        c.drawString(*mm_to_pt(160, 12 + offset_y), f"{mes_ano[1]}/{mes_ano[0]}")

        # Nome e Cargo
        c.drawString(*mm_to_pt(10, 19 + offset_y), folha["nome"])
        c.drawString(*mm_to_pt(10, 23 + offset_y), folha["cargo"])

        # CBO, matrícula, admissão
        c.drawString(*mm_to_pt(125, 17 + offset_y), "422110")
        c.drawString(*mm_to_pt(125, 21 + offset_y), "Admissão:")
        c.drawString(*mm_to_pt(150, 21 + offset_y), folha["data_admissao"])

        # Tabela de rubricas
        rubricas = [
            ("8781", "SALARIO", "30,00", folha["salario_base"], ""),
            ("995", "SALARIO FAMILIA", "1", folha["beneficios"], ""),
            ("998", "I.N.S.S.", "8,00", "", 87.56),
            ("048", "VALE TRANSPORTE", "6,00", "", 65.67),
        ]

        y = 30 + offset_y
        for cod, desc, ref, venc, descs in rubricas:
            y += 5.0  # Mais compactado
            c.setFont("Courier", 10)  # Fonte monoespaçada como no modelo real

            c.drawString(*mm_to_pt(3, y), cod)
            c.drawString(*mm_to_pt(17, y), desc)

            x_ref, y_ref = mm_to_pt(115, y)
            c.drawRightString(x_ref, y_ref, ref)

            if venc:
                c.drawRightString(
                    mm_to_pt(140, y)[0],
                    mm_to_pt(0, y)[1],
                    f"{venc:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )
            if descs:
                c.drawRightString(
                    mm_to_pt(165, y)[0],
                    mm_to_pt(0, y)[1],
                    f"{descs:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )

        # Totais
        total_venc = folha["salario_base"] + folha["beneficios"]
        total_desc = 87.56 + 65.67
        liquido = total_venc - total_desc

        y_totais = y + 22  # Espaço para os totais

        c.setFont("Courier", 10)
        c.drawRightString(
            *mm_to_pt(168, y_totais),
            f"{total_venc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawRightString(
            *mm_to_pt(168, y_totais + 30),
            f"{total_desc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
        c.drawRightString(
            *mm_to_pt(168, y_totais + 38),
            f"{liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )

        # Escritório de contabilidade (rodapé)
        c.setFont("Times-Roman", 11)
        c.drawString(*mm_to_pt(3, y_totais + 35), folha["escritorio"])

    # Imprime 2 holerites por página
    desenhar_holerite(offset_y=0)
    desenhar_holerite(offset_y=140)

    c.save()

    modelo = fitz.open(MODELO_PDF)
    overlay = fitz.open(temp_overlay_path)
    page = modelo[0]
    page.show_pdf_page(page.rect, overlay, 0)
    modelo.save(caminho_saida)
    modelo.close()
    overlay.close()

    if os.path.exists(temp_overlay_path):
        os.remove(temp_overlay_path)

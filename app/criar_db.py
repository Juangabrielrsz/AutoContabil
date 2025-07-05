import sqlite3


def adicionar_colunas_se_nao_existirem():
    conn = sqlite3.connect("app/database.db")
    cursor = conn.cursor()

    # Obter informações das colunas existentes na tabela
    cursor.execute("PRAGMA table_info(folha_pagamento)")
    colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]

    # Lista de colunas que queremos garantir que existam
    colunas_desejadas = {"empresa": "TEXT", "escritorio": "TEXT"}

    # Verifica e adiciona cada coluna, se necessário
    for coluna, tipo in colunas_desejadas.items():
        if coluna not in colunas_existentes:
            print(f"Adicionando coluna '{coluna}' na tabela folha_pagamento...")
            cursor.execute(f"ALTER TABLE folha_pagamento ADD COLUMN {coluna} {tipo}")

    conn.commit()
    conn.close()
    print("Verificação e ajuste concluídos.")


if __name__ == "__main__":
    adicionar_colunas_se_nao_existirem()

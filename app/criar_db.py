import sqlite3

conn = sqlite3.connect("app\database.db")  # ajuste o caminho se necessário
cursor = conn.cursor()

# Apagar tabela antiga, se existir
cursor.execute("DROP TABLE IF EXISTS extratos")

# Criar nova tabela com CNPJ
cursor.execute(
    """
    CREATE TABLE extratos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        cnpj TEXT NOT NULL,
        descricao TEXT NOT NULL,
        data TEXT NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL
    )
    """
)

conn.commit()
conn.close()
print("Tabela antiga removida e nova tabela 'extratos' criada com sucesso.")

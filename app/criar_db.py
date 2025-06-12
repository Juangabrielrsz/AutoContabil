import sqlite3
import os

# Caminho do banco
db_path = os.path.join("app", "database.db")
os.makedirs("app", exist_ok=True)

# Conexão
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criação da tabela de notas fiscais
cursor.execute(
    """
CREATE TABLE extratos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    descricao TEXT NOT NULL,
    data TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor REAL NOT NULL
)
"""
)

conn.commit()
conn.close()
print("Banco de dados e tabela criados com sucesso.")

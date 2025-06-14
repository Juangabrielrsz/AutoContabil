import sqlite3

conn = sqlite3.connect("app/database.db")  # ou seu caminho correto
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS mei (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha_gov TEXT NOT NULL,
    cnpj TEXT NOT NULL
)
"""
)

conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect("app/database.db")
cursor = conn.cursor()

# Adiciona a coluna 'cpf' se ela ainda não existir
try:
    cursor.execute("ALTER TABLE mei ADD COLUMN cpf TEXT")
except sqlite3.OperationalError:
    print("Coluna 'cpf' já existe.")

conn.commit()
conn.close()

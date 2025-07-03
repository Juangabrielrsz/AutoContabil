import sqlite3

conn = sqlite3.connect("app/database.db")  # ou seu caminho correto
cursor = conn.cursor()

cursor.execute("ALTER TABLE colaboradores ADD COLUMN status TEXT")
conn.commit()
conn.close()

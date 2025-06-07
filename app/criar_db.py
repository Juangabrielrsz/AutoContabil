import sqlite3
import os

# Caminho do banco
db_path = os.path.join("app", "database.db")
os.makedirs("app", exist_ok=True)

# Conexão
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criação da tabela de notas fiscais
cursor.execute('''
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo TEXT,
    emitente TEXT,
    cnpj TEXT,
    numero TEXT,
    data_emissao TEXT,
    valor_total REAL
)
''')

conn.commit()
conn.close()
print("Banco de dados e tabela criados com sucesso.")

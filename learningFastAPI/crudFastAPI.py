# Cenário: Sistema de biblioteca comunitária
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

"""
+ O fluxo padrão para enviar qualquer comando é sempre este:
1 - Abre a conexão.
2 - Cria o cursor.
3 - Usa o cursor.execute("SEU COMANDO SQL AQUI").
4 - Se o comando alterou dados (como criar tabelas ou inserir), você dá um conexao.
5 - commit() para salvar no arquivo físico.
6 - Fecha o cursor e a conexão.
"""

connection = sqlite3.connect("biblioteca.db")
cursor = connection.cursor()

# Cria a tabela "livros"
cursor.execute("""
CREATE TABLE IF NOT EXISTS livros(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    paginas INTEGER NOT NULL
);
""")

connection.commit()
cursor.close()
connection.close()

# Instanciando o objeto "app" à classe FastAPI()
app = FastAPI()

class Livro(BaseModel):
    nome: str
    autor:str
    paginas: int

@app.post("/livros/")
def criar_livros(livro_recebido: Livro):
    commandSQL = "INSERT INTO livros (titulo, autor, paginas) VALUES (?, ?, ?);"
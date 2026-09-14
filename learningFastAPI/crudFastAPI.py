# Cenário: Sistema de biblioteca comunitária
from fastapi import FastAPI, HTTPException, status
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

# Essa classe Livro pega o JSON e valida os dados, sendo cada atributo um tipo de filtro
class Livro(BaseModel):
    titulo: str
    autor:str
    paginas: int

class AtualizarPaginas(BaseModel): # Exclusivo do Patch
    paginas: int  # O campo que o usuário vai enviar no JSON    


@app.post("/livros/", status_code=status.HTTP_200_OK) # O create do CRUD
def criar_livros(livro_recebido: Livro):

    commandSQL = "INSERT INTO livros (titulo, autor, paginas) VALUES (?, ?, ?);"
    dados = (livro_recebido.titulo, livro_recebido.autor, livro_recebido.paginas)

    # Abre conexão
    connection = sqlite3.connect("biblioteca.db")

    # Cria o cursor
    cursor = connection.cursor()

    # Executa o comando
    cursor.execute(commandSQL, dados)

    # commit() para salvar
    connection.commit()

    # Fecha o cursor e conexão
    cursor.close()
    connection.close()

    # Retorna um JSON
    return {"mensagem": "Livro criado com todo sucesso do mundo!"}


@app.get("/livros/", status_code=status.HTTP_200_OK) # O read do CRUD
def obter_livros():
    # Abre conexão
    connection = sqlite3.connect("biblioteca.db")

    # Cria o cursor
    cursor = connection.cursor()

    # Executa o comando
    cursor.execute("SELECT id, titulo, autor, paginas FROM livros;")

    # Guarda resultado em uma variável
    livros_obtidos: list = cursor.fetchall()

    # Fecha o cursor e conexão
    cursor.close()
    connection.close()

    # Retorna um JSON
    return {
        "mensagem": "Livros obtidos com todo o sucesso do mundo!",
        "dados": livros_obtidos
}

@app.get("/livros/{livro_id}", status_code=status.HTTP_200_OK)
def obter_livro_especifico(livro_id: int):
    commandSQL = "SELECT * FROM livros WHERE id = ?;"
    dados = (livro_id,)
    mensagem = f"O livro do id {livro_id} foi acessado com todo o sucesso do mundo!"
        
    # Abre conexão
    connection = sqlite3.connect("biblioteca.db")
    
    # Cria o cursor
    cursor = connection.cursor()
    
    # Executa o comando
    cursor.execute(commandSQL, dados)
    
    # Guarda resultado em uma variável
    livros_obtido: list = cursor.fetchone()
    
    # Fecha o cursor e conexão
    cursor.close()
    connection.close()

    return {
        "mensagem": mensagem,
        "dados": livros_obtido
}

@app.delete("/livros/{livro_id}") # O delete do CRUD
def deletar_livros(livro_id: int):

    commandSQL: str = """
    DELETE FROM livros
    WHERE id = ?;
"""

    dados = (livro_id,)

    connection = sqlite3.connect("biblioteca.db")
    cursor = connection.cursor()

    cursor.execute(commandSQL, dados)

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "mensagem": "O livro foi deletado com todo o sucesso do mundo!"
    }


@app.patch("/livros/{livro_id}")
def atualizar_livros(livro_id: int, qtd_pagina: AtualizarPaginas):

    commandSQL: str = """
    UPDATE livros
    SET paginas = ?
    WHERE id = ?;
"""

    dados: tuple[int, int] = (qtd_pagina.paginas, livro_id)

    connection = sqlite3.connect("biblioteca.db")
    cursor = connection.cursor()

    cursor.execute(commandSQL, dados)

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "mensagem": "Livro atualizado com todo o sucesso do mundo!",
        "id_livro_atualizado": livro_id,
        "quantidade_de_paginas": qtd_pagina.paginas
    }



@app.put("/livros/{livro_id}")
def mudar_livros(livro_id: int, livro_novo: Livro):
    
    commandSQL: str = """
    UPDATE livros
    SET titulo = ?, autor = ?, paginas = ?
    WHERE id = ?;
"""

    dados: tuple[str, str, int, int] = (livro_novo.titulo, livro_novo.autor, livro_novo.paginas, livro_id)

    connection = sqlite3.connect("biblioteca.db")
    cursor = connection.cursor()

    cursor.execute(commandSQL, dados)

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "mensagem": "Livro mudado com todo sucesso do mundo!",
        "livro_id": livro_id,
        "livro_novo": livro_novo
    }

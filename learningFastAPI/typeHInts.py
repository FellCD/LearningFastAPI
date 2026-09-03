# O type hint é um recurso do Python que permite você declarar o tipo da variável
from datetime import date
from pydantic import BaseModel, EmailStr, HttpUrl

def soma_dois_numeros(a: int, b: int) -> int: # Type Hints aqui, a estrutura é variável: tipo de dado
    return a + b

caso1 = soma_dois_numeros(1,1)
print(caso1)

# O type hint é importante no FastAPI pois ajuda na Auto Swagger dele

# Tipos de dados

class UsuarioCadastro(BaseModel): # O BaseModel ja faz o método __init__ e ainda valida dados e converte dict para JSON e vice-versa
    # Campos obrigatórios com tipos primitivos e especiais
    nome: str
    idade: int
    email: EmailStr  # <- Valida o e-mail sozinho e especial do Pydantic
    
    # Campo opcional (pode ser None se não for enviado) --- | é para valor Default
    telefone: str | None = None
    
    # Validações avançadas do Pydantic
    site_pessoal: HttpUrl | None = None
    data_nascimento: date
    
    # Coleção de dados (lista de textos) A estrutura é list[tipo de dado, tipo de dado, tipo de dado...]
    hobbies: list[str] = []

    # Coleção de dados (Dict) A estutura é dict[tipo de dado chave: tipo de dado valor]
    livros: dict[str, str]
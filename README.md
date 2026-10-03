# Music and Playlist API

API RESTful desenvolvida com **FastAPI** e **SQLite3** para gerenciamento de músicas, playlists e seus vínculos.

---

## Sobre o Projeto

Este projeto consiste em uma API modularizada em Python para cadastrar e organizar músicas em playlists. O objetivo principal foi aplicar boas práticas de arquitetura de código, separação de responsabilidades (Routers, Schemas, Database) e manipulação de banco de dados relacional com SQL puro.

### Tecnologias Utilizadas

* **Python 3**
* **FastAPI** (Framework web)
* **Uvicorn** (Servidor ASGI)
* **SQLite3** (Banco de dados relacional)
* **Pydantic** (Validação de dados)

---

## Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o Python instalado na sua máquina.

### Passo a Passo

1. **Clonar o repositório:**
   git clone https://github.com/FellCD/learningFastAPI.git
   cd learningFastAPI

2. **Criar e ativar o ambiente virtual:**
   python -m venv .venv
   # No Linux/macOS:
   source .venv/bin/activate
   # No Windows:
   .venv\Scripts\activate

3. **Instalar as dependências:**
   pip install -r requirements.txt

4. **Executar a aplicação:**
   fastapi dev src/main.py
   # Ou via uvicorn:
   uvicorn src.main:app --reload

5. **Acessar a documentação:**
   Abra o navegador em http://127.0.0.1:8000/docs para testar os endpoints interativamente via Swagger UI.

---

## Estrutura do Projeto

* **src/** == Pasta raiz do codigo fonte (ou Source-code)
* **src/database.py** == Configuração, criação e conexão do Banco de Dados
* **src/main.py** == É o ponto de partida da aplicação
* **routers/** == Pasta que organiza as rotas e endpoints
* **routers/songs.py** == Tem as rotas e endpoints relacionadas as músicas isoladas e tem prefixo "/songs"
* **routers/playlists.py** == Tem as rotas e endpoints das playlists, podendo criar, alterar e listar elas. Tem prefixo "/playlists"
* **routers/playlists_songs.py** == Responsável pelas rotas de conexão (vínculos ou associações) entre playlists e songs, podendo adicionar músicas em playlists, listar quais músicas pertencem a qual playlist e etc. Tem prefixo "/playlists_songs"
* **schemas/** == Pasta que tem por função validar dados, tipagem e outras funcionalidades utilizando o Pydantic. Garantindo integridade dos dados.
* **schemas/songSchema** == Validação de tipo das músicas 
* **schemas/playlistSchema** == Validação de tipo das playlists
---

## Endpoints Principais

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| GET | /songs | Lista todas as músicas |
| GET | /playlists | Lista todas as playlists |
| GET | /playlists-songs/{id} | Traz os detalhes da playlist e suas músicas |

# Cenário: Sistema de musicas e playlist

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from pathlib import Path
import sqlite3

# Pega o diretório onde este arquivo .py está localizado e aponta para o songs.db nele
DB_PATH = Path(__file__).parent / "songs.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Criação da tabela "songs": id(pkey int), name(text), duration_second(int) 
cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        author TEXT NOT NULL,
        duration_second INTEGER NOT NULL
    );
""")

# Criação da tabela "playlists": id(pkey int), playlist_name(text)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_name TEXT NOT NULL
    );
""")

# Criação da tabela "playlists_songs": id(pkey int), playlist_id(fkey - playlists(id)), song_id(fkey - songs(id))
cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists_songs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER,
        song_id INTEGER ,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id),
        FOREIGN KEY (song_id) REFERENCES songs(id)
    );
""")

connection.commit()
cursor.close()
connection.close()

# Schemas da Música
class DurationSchema(BaseModel):
    duration_min: int
    duration_sec: int

class SongSchema(BaseModel):
    name: str
    author: str
    duration: DurationSchema

class UpdateSongSchema(BaseModel):
    name: str | None = None
    author: str | None = None
    duration:DurationSchema | None = None


# Instância do objeto "app" para classe FastAPI()
app = FastAPI()

# Endpoints da música em si (Song)

# Endpoint do Verbo POST para adicionar músicas
@app.post("/songs/", status_code=status.HTTP_201_CREATED)
def add_song(song: SongSchema):

    # Declaração das variáveis antes do Try
    connection = None
    cursor = None

    try: # Final Bom

        seconds_total = (song.duration.duration_min * 60) + song.duration.duration_sec

        # Definição dos dados
        commandSQL: str = """INSERT INTO songs (name, author, duration_second) VALUES (?, ?, ?);"""
        dados: tuple[str, str, int] = (song.name, song.author, seconds_total)

        # Abre conexão
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Executa comandos
        cursor.execute(commandSQL, dados)

        # Salva as informações
        connection.commit()

        return {
            "status": "sucesso!",
            "mensagem": f"A música {song.name} foi adicionada com todo o sucesso do mundo!"
        }

    # Final Ruim: Erro do banco
    except sqlite3.Error as e:
        if connection: # Se connection estiver ativa
            connection.rollback() # Desfaz algo se deu errado no meio da execução

        # Avisa ao cliente/frontend sobre o status da situação
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    # Final Ruim: Erro Genérico
    except Exception as e:
        if connection:
            connection.rollback()

        # Avisa ao cliente/frontend sobre o status da situação
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )
        

    finally: # Inevitável

        # Fecha o cursor
        if cursor: # Se o Cursor estiver ativo, feche-a
            cursor.close()

        # Fecha a conexão
        if connection: # Se a conexão estiver ativa, feche-a
            connection.close()

# Endpoint do Verbo GET para obter a música por ID dela
@app.get("/songs/{song_id}", status_code=status.HTTP_200_OK)
def get_song_by_id(song_id: int):

    # Declara as variáveis antes do try
    connection = None
    cursor = None

    try: # Final Bom

        # Abre conexão
        connection = sqlite3.connect(DB_PATH)

        # connection.row_factory é para o mapeamento de linha por nome de coluna
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        # Definição dos dados
        commandSQL: str = """SELECT * FROM songs WHERE id = ?"""
        dados: tuple[int] = (song_id,)

        # Executa comandos
        cursor.execute(commandSQL, dados)

        # Obtém o resultado em uma lista
        obtained_song: tuple | None = cursor.fetchone()

        # Verificação da lista: se não existe (None) | Regra de Negócio
        if obtained_song is None:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= "Erro de requisição: A música não existe!"
            )

        return {
            "status": "sucesso!",
            "mensagem": dict(obtained_song)
        }

    # Final Ruim: Erro do banco
    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        # Avisa cliente/frontend sobre o status da situação
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    # Final Ruim: Erro Genérico
    except Exception as e:
        if connection:
            connection.rollback()

        # Avisa cliente/frontend sobre o status da situação
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno {str(e)}",
        )


    finally: # Inevitável

        # Fecha o cursor
        if cursor:
            cursor.close()

        # Fecha a conexão
        if connection:
            connection.close()

# Endpoint do Verbo DELETE para deletar a música de acordo com seu ID
@app.delete("/songs/{song_id}", status_code=status.HTTP_200_OK)
def delete_song_by_id(song_id: int):

    connection = None
    cursor = None

    # Final Bom
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        commandSQL: str = """DELETE FROM songs WHERE id = ?"""
        dados: tuple[int] = (song_id,)

        cursor.execute(commandSQL, dados)
    
        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Música não encontrada"
            )

        connection.commit()

        return {
            "status": "Sucesso!",
            "mensagem": f"A música do ID {song_id} foi deletada com todo o sucesso do mundo!"
        }

    # Garante a integridade do erro 404 que estava no bloco do Try
    except HTTPException:
        if connection:
            connection.rollback()

        raise # Retorna o erro especifico do Try para não ser sobrescrever o erro do Try (404 nesse caso)

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if connection:
            connection.rollback()

        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    #Inevitável
    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# Endpoint do Verbo PATCH para atualizar um campo da tabela de songs
@app.patch("/songs/{song_id}", status_code=status.HTTP_200_OK)
def update_song_by_id(song_id: int, newSong: UpdateSongSchema):

    connection = None
    cursor = None

    # Converte os dados do cliente em um Dict
    dados_enviados: dict = newSong.model_dump(exclude_unset=True) # O valor default "exclude_unset=True" define que valores vazios não serão representados por None e ignorados

    # Se estiver vazio (dict vazio ou {})
    if not dados_enviados: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado fornecido!",
        )

    # Final Bom
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        clausulas_set: list = []
        valores: list = []

        # Percorre o Dict "dados_enviados" com chave e valor (o .items() traz chave(str) e valor(any) em tupla)
        for k, v in dados_enviados.items():

            if k == "name": # "k" sempre é uma String
                clausulas_set.append("name = ?")
                valores.append(v) # "v" é String ("Ex": ["Yesterday", "Wave", "Samba do Avião"])

            if k == "author": # "k" é String
                clausulas_set.append("author = ?")
                valores.append(v) # "v" é String ("Ex": ["The Beatles, Tom Jobim, "Gal Costa"])

            if k == "duration": # "k" é String
                # Transformar o dict em um valor normal, sem ser coleção
                total_sec = (v["duration_min"] * 60) + v["duration_sec"] # "v" é um Dict aqui, pois o Schema do duration é um dict
                clausulas_set.append("duration_second = ?")
                valores.append(total_sec) # Não adiciona-se "v" para não colocar um dict dentro de dict e para poder botar no SQL

        valores.append(song_id) # O "song_id" que é int é para botar no parâmetro WHERE

        # Comandos
        commandSQL: str = f"UPDATE songs SET {', '.join(clausulas_set)} WHERE id = ?"
        
        cursor.execute(commandSQL, tuple(valores))

        # Se nada foi afetado, a música não existe
        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Música com id {song_id} não encontrada!",
            )

        # Salva as alterações
        connection.commit()

        # Retorno do JSON
        return {
            "status": "Sucesso!",
            "mensagem": "Música atualizada com todo sucesso do mundo!"
        }

    except HTTPException:
        if connection:
            connection.rollback()

        raise # Relança o erro do Try (Regra de Negócio)

    except sqlite3.Error as e:
        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if connection:
            connection.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

# Schemas de Playlist
class PlaylistCreate(BaseModel):
    playlist_name: str

class PlaylistUpdate(BaseModel):
    playlist_name: str | None

@app.post("/playlists/", status_code=status.HTTP_201_CREATED)
def add_playlist(playlist: PlaylistCreate):
    conn = None
    cursor = None

    try:
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        commandSQL: str = """INSERT INTO playlists (playlist_name) VALUES (?);"""
        dados: tuple[str] = (playlist.playlist_name,)

        cursor.execute(commandSQL, dados)
        playlist_id = cursor.lastrowid

        conn.commit()

        return {
            "status": "Sucesso!",
            "mensagem": f"A playlist {playlist.playlist_name} foi criada com todo o sucesso do mundo!",
            "dados": {
                "id": playlist_id,
                "name": playlist.playlist_name
            }
        }

    except sqlite3.Error as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )


    finally:
        if cursor:
            cursor.close()
        
        if conn:
            conn.close()

@app.get("/playlists/", status_code=status.HTTP_200_OK)
def get_playlist():

    conn = None
    cursor = None

    try:
        # Liga a conexão
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # connection.row_factory é para o mapeamento de linha por nome de coluna
        cursor = conn.cursor()

        commandSQL: str = "SELECT * FROM playlists;"

        cursor.execute(commandSQL)
        rows = cursor.fetchall() # Obtém todos os registros

        playlist: list = [dict(row) for row in rows] # A coleção "playlist" converte os registros em formato Dict

        # Mensagem estilizada caso não tenha registros
        if not playlist:
            return {
                "status": "sucesso!",
                "mensagem": "Não há playlists cadastradas!",
                "dados": []
            } 

        return {
            "status": "sucesso!",
            "mensagem": "Playlists obtidas com todo o sucesso do mundo!",
            "dados": playlist
        }

    except sqlite3.Error as e:
        if conn:
            conn.rollback()

        raise HTTPException(
                status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= f"Erro Interno: {str(e)}",
            )

    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

@app.get("/playlists/{playlist_id}", status_code=status.HTTP_200_OK)
def get_playlist_by_id(playlist_id: int):
    conn = None
    cursor = None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        commandSQL: str = "SELECT * FROM playlists WHERE id = ?;"
        dados: tuple[int] = (playlist_id,)
        cursor.execute(commandSQL, dados)
        obtained_playlist: tuple | None = cursor.fetchone()

        if obtained_playlist is None:

            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= "Erro de requisição: A playlist não existe!"
            )

        return {
            "status": "sucesso!",
            "mensagem": "Playlist obtida com todo o sucesso do mundo!",
            "dados": dict(obtained_playlist)
        }

    # Garante a integridade do erro 404 que estava no bloco do Try
    except HTTPException:
        raise # Retorna o erro especifico do Try para não ser sobrescrever o erro do Try (404 nesse caso)
    

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )


    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

@app.delete("/playlists/{playlist_id}", status_code=status.HTTP_200_OK)
def delete_playlist_by_id(playlist_id: int):
    conn = None
    cursor = None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        commandSQL: str = "DELETE FROM playlists WHERE id = ?;"
        dados: tuple[int] = (playlist_id,)
        cursor.execute(commandSQL, dados)

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Playlist não encontrada!"
             )

        conn.commit()

        return {
            "status": "sucesso!",
            "mensagem": f"playlist {playlist_id} foi deletada com todo o sucesso do mundo!"
        }

    except HTTPException:
        if conn:
            conn.rollback()
        
        raise

    except sqlite3.Error as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Erro Interno: {str(e)}"
        )
    
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

@app.patch("/playlists/{playlist_id}", status_code=status.HTTP_200_OK)
def update_playlist_by_id(playlist_id: int, newPlaylist: PlaylistUpdate):
    conn = None
    cursor = None

    dados_enviados: dict = newPlaylist.model_dump(exclude_unset=True)

    if not dados_enviados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado fornecido!",
        )

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        clausulas_set: list = []
        valores: list = []

        for k, v in dados_enviados.items():
            if k == "playlist_name":
                clausulas_set.append(f"{k} = ?")
                valores.append(v)

        valores.append(playlist_id)

        commandSQL: str = f"UPDATE playlists SET {', '.join(clausulas_set)} WHERE id = ?"
                
        cursor.execute(commandSQL, tuple(valores))

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= f"A playlist {playlist_id} não existe!",
            )

        conn.commit()

        return {
            "status": "sucesso!",
            "mensagem": "Playlist atualizada com todo sucesso do mundo!"
        }
    
    except HTTPException:
        if conn:
            conn.rollback()
        
        raise # HTTP 404

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

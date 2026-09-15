# Cenário: Sistema de musicas e playlist

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3

connection = sqlite3.connect("songs.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        author TEXT NOT NULL,
        duration_second INTEGER NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_name TEXT NOT NULL
    );
""")

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

class DurationSchema(BaseModel):
    duration_min: int
    duration_sec: int

class SongSchema(BaseModel):
    name: str
    author: str
    duration: DurationSchema


app = FastAPI()


# Verbo POST para adicionar músicas
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
        connection = sqlite3.connect("songs.db")
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
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= f"Erro de requisição de inserção: {str(e)}",
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
        if cursor:
            cursor.close()

        # Fecha a conexão
        if connection:
            connection.close()



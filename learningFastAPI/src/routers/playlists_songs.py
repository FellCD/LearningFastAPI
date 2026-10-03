import sqlite3
from fastapi import APIRouter, HTTPException, status
from src.database import DB_PATH

# Roteador de API de Playlists_Songs
router = APIRouter(prefix="/playlists-songs", tags=["Playlist Songs"])

# Ponte entre playlists (tabela pai) e songs (tabela filho)

# Endpoint do verbo POST para criar relação entre playlist e música via IDs
@router.post("/{playlist_id}/songs/{song_id}", status_code=status.HTTP_201_CREATED)
def add_song_to_playlist(playlist_id: int, song_id: int):
    connector = None
    cursor = None

    try:
        connector = sqlite3.connect(DB_PATH)
        connector.execute("PRAGMA foreign_keys = ON;")
        cursor = connector.cursor()

        commandSQL: str = "SELECT id FROM playlists WHERE id = ?;"
        dados: list[int] = [playlist_id]
        cursor.execute(commandSQL, dados)

        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Playlist {playlist_id} não foi encontrada!",
            )

        commandSQL: str = "SELECT id FROM songs WHERE id = ?;"
        dados: list[int] = [song_id]
        cursor.execute(commandSQL, dados)

        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Música {song_id} não foi encontrada!",
            )

        commandSQL: str = "INSERT INTO playlists_songs (playlist_id, song_id) VALUES(?, ?);"
        dados: list = [playlist_id, song_id]
        cursor.execute(commandSQL, dados)

        connector.commit()

        return {
            "status": "sucesso!",
            "mensagem": f"Música {song_id} foi adicionada à playlist {playlist_id}!"
        }

    except sqlite3.IntegrityError as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Música ja está registrada na playlist: {str(e)}",
        )

    except HTTPException:
        if connector:
            connector.rollback()

        raise

    except sqlite3.Error as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()

        if connector:
            connector.close()

# Endpoint do verbo GET para obter relações de playlist e música de modo específico e info de músicas
@router.get("/{playlist_id}", status_code=status.HTTP_200_OK)
def get_playlist_songs(playlist_id: int):
    connector = None
    cursor = None

    try:
        # Abrir conexão e permitir fkeys
        connector = sqlite3.connect(DB_PATH)
        connector.execute("PRAGMA foreign_keys = ON;")
        cursor = connector.cursor()

        # Dando select primeiro para checar existência
        commandSQL: str = "SELECT * FROM playlists WHERE id = ?;"
        dados: tuple[int] = (playlist_id,)
        cursor.execute(commandSQL, dados)
        playlist: tuple = cursor.fetchone()

        # if not pega qualquer valor falso
        if not playlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Playlist {playlist_id} não encontrada!",
            )

        # Cruzar informações com JOIN
        commandSQL: str = "SELECT songs.id, songs.name, songs.author, songs.duration_second FROM songs INNER JOIN playlists_songs ON songs.id = playlists_songs.song_id WHERE playlists_songs.playlist_id = ?"
        cursor.execute(commandSQL, dados)
        rows: list = cursor.fetchall()
        songs: list = [{"id": row[0], "name": row[1], "author": row[2], "duration_second": row[3]} for row in rows]

        return {
            "status": "sucesso!",
            "dados": {
                "playlist_id": playlist[0],
                "playlist_name": playlist[1],
                "total_songs": len(songs),
                "songs": songs
            }
        }

    except HTTPException:
        if connector:
            connector.rollback()

        raise # 404

    except sqlite3.Error as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()

        if connector:
            connector.close()

# Endpoint do verbo DELETE para deletar relação entre playlist e música via IDs
@router.delete("/{playlist_id}/songs/{song_id}", status_code=status.HTTP_200_OK)
def delete_playlist_songs(playlist_id: int, song_id: int):
    connector = None
    cursor = None

    try:
        connector = sqlite3.connect(DB_PATH)
        connector.execute("PRAGMA foreign_keys = ON;")
        cursor = connector.cursor()

        commandSQL: str = "SELECT 1 FROM playlists_songs WHERE playlist_id = ? AND song_id = ?;"
        dados: tuple[int, int] = (playlist_id, song_id)
        cursor.execute(commandSQL, dados)
        association: tuple = cursor.fetchone()

        if not association:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Não foi encontrada relação com a música {song_id} com a playlist {playlist_id}",
            )

        commandSQL: str = "DELETE FROM playlists_songs WHERE playlist_id = ? AND song_id = ?"
        cursor.execute(commandSQL, dados)
        connector.commit()

        return {
            "status": "sucesso!",
            "mensagem": f"A relação entre a música {song_id} com a playlist {playlist_id} foi deletada com todo o sucesso do mundo!"
        } 

    except HTTPException:
        if connector:
            connector.rollback()

        raise

    except sqlite3.Error as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}",
        )

    except Exception as e:
        if connector:
            connector.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()

        if connector:
            connector.close()

@router.get("", status_code=status.HTTP_200_OK)
def get_all_playlist_songs():
    connector = None
    cursor = None

    try:
        connector = sqlite3.connect(DB_PATH)
        connector.execute("PRAGMA foreign_keys = ON;")
        cursor = connector.cursor()

        # Seleciona todos os pares de IDs vinculados na tabela ponte
        commandSQL: str = "SELECT playlist_id, song_id FROM playlists_songs;"
        cursor.execute(commandSQL)
        rows: list = cursor.fetchall()

        # Monta a lista com os dicionários de cada relação (row[0] = playlist_id, row[1] = song_id)
        relations: list[dict] = [
            {"playlist_id": row[0], "song_id": row[1]} for row in rows
        ]

        return {
            "status": "sucesso!",
            "mensagem": "Relações entre playlists e músicas obtidas com sucesso!",
            "total_relations": len(relations),
            "dados": relations,
        }

    except sqlite3.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro Interno: {str(e)}",
        )

    finally:
        if cursor:
            cursor.close()
            
        if connector:
            connector.close()

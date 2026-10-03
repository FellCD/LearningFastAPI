import sqlite3
from fastapi import APIRouter, HTTPException, status
from src.database import DB_PATH
from src.schemas.playlistSchema import PlaylistCreate, PlaylistUpdate

# Roteador de API de Playlists
router = APIRouter(prefix="/playlists", tags=["Playlists"])

# Endpoint do verbo POST para criar uma playlist
@router.post("", status_code=status.HTTP_201_CREATED)
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

# Endpoint do verbo GET para obter dados de todas as playlists
@router.get("", status_code=status.HTTP_200_OK)
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

# Endpoint do verbo GET para obter dados de uma playlist de acordo com seu ID
@router.get("/{playlist_id}", status_code=status.HTTP_200_OK)
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

# Endpoint do verbo DELETE para deletar a playlist de acordo com seu ID
@router.delete("/{playlist_id}", status_code=status.HTTP_200_OK)
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

# Endpoint do verbo PATCH para atualizar dinamicamente a playlist de acordo com seu ID
@router.patch("/playlists/{playlist_id}", status_code=status.HTTP_200_OK)
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

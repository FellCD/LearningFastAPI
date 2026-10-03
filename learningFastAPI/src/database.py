from pathlib import Path
import sqlite3

# Pega o diretório onde este arquivo .py está localizado e aponta para o songs.db nele
DB_PATH = Path(__file__).parent / "songs.db"

def init_db():
    
    """Cria as tabelas do banco de dados caso elas ainda não existam."""
    connector = None
    cursor = None

    try:
        connector = sqlite3.connect(DB_PATH)
        connector.execute("PRAGMA foreign_keys = ON;")
        cursor = connector.cursor()

        # Tabela de Músicas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                author TEXT NOT NULL,
                duration_second INTEGER NOT NULL
            );
        """
        )

        # Tabela de Playlists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """
        )

        # Tabela Ponte (Join Table)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlists_songs (
                playlist_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                PRIMARY KEY (playlist_id, song_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
            );
        """
        )

        connector.commit()

    except sqlite3.Error as e:
        if connector:
            connector.rollback()
        print(f"Erro ao inicializar o banco de dados: {e}")

    finally:
        if cursor:
            cursor.close()
        if connector:
            connector.close()

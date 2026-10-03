from pathlib import Path

# Pega o diretório onde este arquivo .py está localizado e aponta para o songs.db nele
DB_PATH = Path(__file__).parent / "songs.db"
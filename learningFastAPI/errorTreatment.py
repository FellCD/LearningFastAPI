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


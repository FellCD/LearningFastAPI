from fastapi import FastAPI
from src.routers import songs, playlists, playlists_songs
from src.database import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Tudo ANTES do 'yield' corre ao LIGAR o servidor (Startup)
    print("\nInicializando a base de dados...\n")
    init_db()

    yield  # A aplicação fica rodando e respondendo pedidos aqui

    # 2. Tudo DEPOIS do 'yield' corre ao DESLIGAR o servidor (Shutdown)
    print("\nFechando ligações e desligando a API...\n")

app = FastAPI(title="Music and Playlist API", lifespan=lifespan)

app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(playlists_songs.router)

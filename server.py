from fastapi import FastAPI
from yt_dlp import YoutubeDL
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from random import choice

urls = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Define the options similar to your yt-dlp command
    ydl_opts = {
        "flat-playlist": True,
        "extract_flat": True,
        "quiet": True,
    }

    playlist_url = "https://music.youtube.com/watch?v=nYEoxne_20Y&list=RDCLAK5uy_m8-hn_Dh2IINzL4vpN_vnafTZflvH30pM"

    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        if result:
            for entry in result["entries"]:
                urls.append(entry["url"])
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://192.168.1.8:5173/",
    "https://a29c-103-203-73-78.ngrok-free.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/getVideo")
def give_video_info():
    ydl_opts = {
        "format": "m4a/bestaudio/best",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(choice(urls), download=False)
        if info:
            return info["url"], info["title"]
        else:
            return None

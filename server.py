from fastapi import FastAPI
from yt_dlp import YoutubeDL
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from requests_html import HTML
from fake_useragent import UserAgent
from httpx import AsyncClient
from random import choice
import asyncio


urls = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Define the options similar to your yt-dlp command
    ydl_opts = {
        "flat-playlist": True,
        "extract_flat": True,
        "quiet": True,
    }

    playlist_url = (
        "https://www.jiosaavn.com/featured/weekend-sadhya/Kl3SldGMVC5uOxiEGmm6lQ__"
    )

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

headers = {"User-Agent": UserAgent().firefox}

client = AsyncClient()


@app.get("/getVideo")
async def give_video_info():
    ydl_opts = {
        "format": "m4a/bestaudio/best",
    }
    with YoutubeDL(ydl_opts) as ydl:
        url = choice(urls)
        response = await client.get(url, headers=headers)
        html = HTML(html=response.text)
        title = html.find(".u-h2", first=True).text
        info = await asyncio.to_thread(ydl.extract_info, url, download=False)
        if info:
            return info["url"], title
        else:
            return None

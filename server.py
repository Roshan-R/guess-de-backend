from fastapi import FastAPI
from yt_dlp import YoutubeDL
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from requests_html import HTML
from fake_useragent import UserAgent
from httpx import AsyncClient
from random import choice
import asyncio
from uuid import uuid4


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
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


headers = {"User-Agent": UserAgent().firefox}
client = AsyncClient()
client_map: dict[str, list[str]] = {}
urls = []


@app.get("/terminateClient")
async def terminate(client_id: str):
    del client_map[client_id]


@app.get("/getVideo")
async def give_video_info(client_id: str | None = None):
    if client_id:
        if len(client_map[client_id]) == len(urls):
            blacklist = []
            client_map[client_id] = []
        else:
            blacklist = client_map[client_id]

        url = choice(list(set(urls).difference(blacklist)))
    else:
        client_id = uuid4().__str__()
        url = choice(urls)

    ydl_opts = {
        "format": "m4a/bestaudio/best",
    }

    with YoutubeDL(ydl_opts) as ydl:
        response = await client.get(url, headers=headers)
        html = HTML(html=response.text)
        title = html.find(".u-h2", first=True).text  # type: ignore
        image = html.find("img", first=True).attrs["src"]  # type: ignore
        song_screen_text = html.find(
            'figcaption p:first-of-type [screen_name="song_screen"]', first=True
        ).attrs["title"]  # type: ignore

        client_map.setdefault(client_id, []).append(url)
        info = await asyncio.to_thread(ydl.extract_info, url, download=False)
        return info["url"], title, image, song_screen_text, client_id  # type: ignore

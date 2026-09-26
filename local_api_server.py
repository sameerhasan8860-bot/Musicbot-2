import asyncio
import os
import re
from pathlib import Path

from aiohttp import web
import yt_dlp

HOST = "127.0.0.1"
PORT = int(os.getenv("LOCAL_API_PORT", "8765"))
DOWNLOAD_DIR = Path(os.getenv("LOCAL_API_DOWNLOAD_DIR", "local_api_downloads"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{3,}$")


def video_id_from_url(value: str) -> str:
    if "v=" in value:
        return value.split("v=", 1)[1].split("&", 1)[0]
    if "youtu.be/" in value:
        return value.split("youtu.be/", 1)[1].split("?", 1)[0].split("&", 1)[0]
    return value.strip()


async def download(video_id: str, media_type: str) -> Path | None:
    if not VIDEO_ID_RE.fullmatch(video_id):
        return None

    source = f"https://www.youtube.com/watch?v={video_id}"
    ext = "mp3" if media_type == "audio" else "mp4"
    target = DOWNLOAD_DIR / f"{video_id}.{ext}"

    if target.exists() and target.stat().st_size > 0:
        return target

    loop = asyncio.get_running_loop()

    def work():
        if media_type == "audio":
            opts = {
                "format": "bestaudio/best",
                "outtmpl": str(DOWNLOAD_DIR / f"{video_id}.%(ext)s"),
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        else:
            opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": str(DOWNLOAD_DIR / f"{video_id}.%(ext)s"),
                "merge_output_format": "mp4",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([source])
        except Exception:
            return None

        return target if target.exists() and target.stat().st_size > 0 else None

    return await loop.run_in_executor(None, work)


async def health(request):
    return web.json_response({"status": "ok"})


async def download_handler(request):
    video_id = video_id_from_url(request.query.get("url", ""))
    media_type = request.query.get("type", "audio").lower()

    if media_type not in {"audio", "video"}:
        return web.json_response({"error": "invalid type"}, status=400)

    if not VIDEO_ID_RE.fullmatch(video_id):
        return web.json_response({"error": "invalid url"}, status=400)

    path = await download(video_id, media_type)
    if not path:
        return web.json_response({"error": "download failed"}, status=500)

    return web.FileResponse(path)


async def main():
    app = web.Application(client_max_size=50 * 1024 * 1024)
    app.router.add_get("/health", health)
    app.router.add_get("/download", download_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print(f"Local download API listening on http://{HOST}:{PORT}", flush=True)

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

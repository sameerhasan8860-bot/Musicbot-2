import re

import aiohttp

from AloneX.helpers import Track

_INNERTUBE_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
_INNERTUBE_CLIENT_VERSION = "2.20250101.01.00"
_INNERTUBE_CLIENT_NAME = "WEB"
_VIDEO_ID_RE = re.compile(r"(?i)(?:youtube\.com/(?:watch\?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})")


def _video_id(value: str) -> str:
    if not value:
        return ""
    match = _VIDEO_ID_RE.search(value)
    return match.group(1) if match else (value if re.fullmatch(r"[A-Za-z0-9_-]{11}", value) else "")


def _dig(value, *path):
    cur = value
    for key in path:
        if isinstance(key, int):
            if not isinstance(cur, list) or key >= len(cur):
                return None
            cur = cur[key]
        else:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(key)
    return cur


def _text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if isinstance(value.get("simpleText"), str):
            return value["simpleText"]
        runs = value.get("runs")
        if isinstance(runs, list):
            return "".join(str(x.get("text", "")) for x in runs if isinstance(x, dict))
    return ""


def _duration(value: str) -> int:
    parts = [p for p in (value or "").split(":") if p.isdigit()]
    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return total


def _thumbnail(renderer: dict) -> str:
    thumbs = _dig(renderer, "thumbnail", "thumbnails") or []
    if thumbs and isinstance(thumbs[-1], dict):
        return thumbs[-1].get("url", "")
    return ""


def _track(renderer: dict, video: bool) -> Track | None:
    video_id = renderer.get("videoId")
    title = _text(renderer.get("title"))
    if not video_id or not title:
        return None

    duration = _text(renderer.get("lengthText"))
    channel = _text(renderer.get("ownerText"))
    return Track(
        id=video_id,
        channel_name=channel,
        duration=duration,
        duration_sec=_duration(duration),
        title=title,
        url=f"https://www.youtube.com/watch?v={video_id}",
        thumbnail=_thumbnail(renderer),
        video=video,
    )


def _walk(value, renderer_key: str, out: list[Track], limit: int, video: bool):
    if len(out) >= limit:
        return
    if isinstance(value, list):
        for item in value:
            _walk(item, renderer_key, out, limit, video)
            if len(out) >= limit:
                return
    elif isinstance(value, dict):
        renderer = value.get(renderer_key)
        if isinstance(renderer, dict):
            track = _track(renderer, video)
            if track:
                out.append(track)
                if len(out) >= limit:
                    return
        for child in value.values():
            _walk(child, renderer_key, out, limit, video)
            if len(out) >= limit:
                return


async def _next(payload: dict) -> dict:
    url = f"https://m.youtube.com/youtubei/v1/next?key={_INNERTUBE_KEY}"
    context = {
        "client": {
            "clientName": _INNERTUBE_CLIENT_NAME,
            "clientVersion": _INNERTUBE_CLIENT_VERSION,
            "hl": "en-IN",
            "gl": "IN",
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"context": context, **payload},
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            if response.status >= 400:
                raise RuntimeError(f"YouTube recommendation HTTP {response.status}")
            return await response.json()


async def _mix(video_id: str, limit: int, video: bool) -> list[Track]:
    result = await _next({"playlistId": "RD" + video_id})
    items = _dig(
        result,
        "contents",
        "twoColumnWatchNextResults",
        "playlist",
        "playlist",
        "contents",
    )
    out: list[Track] = []
    _walk(items or [], "playlistPanelVideoRenderer", out, limit, video)
    return out


async def _related(video_id: str, limit: int, video: bool) -> list[Track]:
    result = await _next({"videoId": video_id})
    out: list[Track] = []
    _walk(result, "compactVideoRenderer", out, limit, video)
    if len(out) < limit:
        _walk(result, "videoRenderer", out, limit, video)
    return out


async def candidates(last: Track, limit: int = 10) -> list[Track]:
    video_id = _video_id(last.url or last.id)
    seen: set[str] = set()
    out: list[Track] = []

    if video_id:
        try:
            for track in await _mix(video_id, limit, last.video):
                if track.id not in seen:
                    seen.add(track.id)
                    out.append(track)
        except Exception:
            pass

        if len(out) < limit:
            try:
                for track in await _related(video_id, limit, last.video):
                    if track.id not in seen:
                        seen.add(track.id)
                        out.append(track)
            except Exception:
                pass

    return out

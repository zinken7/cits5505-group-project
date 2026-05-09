# -*- coding: utf-8 -*-
import re
from app.models.media import Media


_SHARE_TAG_RE = re.compile(r"#(.+?)\s+on WatchList Hub\b", re.IGNORECASE)
_TAG_RE = re.compile(r"#([A-Za-z0-9][A-Za-z0-9'&:.,!?\- ]{0,80}[A-Za-z0-9]|[A-Za-z0-9]+)")


def resolve_tags(body: str) -> list[dict]:
    """Extract #Tag patterns from body and resolve against Media titles."""
    matches = _SHARE_TAG_RE.findall(body) or _TAG_RE.findall(body)
    if not matches:
        return []

    seen = set()
    results = []
    for text in matches:
        media, tag_text = _resolve_media_tag(text)
        if not media:
            continue
        if tag_text.lower() in seen:
            continue
        seen.add(tag_text.lower())
        results.append(media_tag(media, text=tag_text))
    return results


def media_tag(media, text=None):
    return {
        "text": text or media.title,
        "media_id": media.id,
        "imdb_id": media.imdb_id,
        "title": media.title,
        "image_url": media.image_url,
        "url": f"/items/{media.imdb_id}" if media.imdb_id else "",
    }


def _resolve_media_tag(text: str):
    """Resolve a greedy hashtag match by trying the longest title prefix first."""
    words = text.strip().split()
    while words:
        candidate = " ".join(words)
        media = Media.query.filter(Media.title.ilike(candidate)).first()
        if media:
            return media, media.title
        words.pop()
    return None, None

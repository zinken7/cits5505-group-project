# -*- coding: utf-8 -*-
import re
from app.models.media import Media


_TAG_RE = re.compile(r"#([A-Za-z0-9][A-Za-z0-9 ]{0,48}[A-Za-z0-9]|[A-Za-z0-9]+)")


def resolve_tags(body: str) -> list[dict]:
    """Extract #Tag patterns from body and resolve against Media titles."""
    matches = _TAG_RE.findall(body)
    if not matches:
        return []

    seen = set()
    results = []
    for text in matches:
        text_stripped = text.strip()
        if text_stripped.lower() in seen:
            continue
        seen.add(text_stripped.lower())
        media = Media.query.filter(Media.title.ilike(text_stripped)).first()
        if media:
            results.append({
                "text": text_stripped,
                "media_id": media.id,
                "imdb_id": media.imdb_id,
                "title": media.title,
                "image_url": media.image_url,
            })
    return results

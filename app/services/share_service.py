# -*- coding: utf-8 -*-
from app.services.friend_service import are_friends
from app.services.media_service import get_media
from app.services.message_service import send_message
from app.services.tag_service import media_tag


def build_share_body(media):
    return f"Check out #{media.title} on WatchList Hub. It's interesting!"


def share_media_with_friends(sender_id, media_id, recipient_ids):
    media = get_media(media_id)
    if not media:
        return None, "Media not found"

    for recipient_id in recipient_ids:
        if not are_friends(sender_id, recipient_id):
            return None, "You can only message friends"

    body = build_share_body(media)
    tags = [media_tag(media)]
    messages = []
    for recipient_id in recipient_ids:
        message, err = send_message(sender_id, recipient_id, body, tags=tags)
        if err:
            return None, err
        messages.append(message)

    return messages, None

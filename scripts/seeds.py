#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seed the database from app/data/.

- Media: every *.json in app/data/ except users.json (movies, anime, tvshow, …).
- Users: app/data/users.json (mock accounts, watchlists, friendships, messages).

Usage:
    python scripts/seeds.py                    # media + users
    python scripts/seeds.py --clear            # wipe media, then load media + users
    python scripts/seeds.py --media-only       # media only
    python scripts/seeds.py --users-only       # users only (needs media for watchlists)
    python scripts/seeds.py --clear --media-only   # e.g. after editing JSON files
    python scripts/seeds.py --type movie      # only seed this media type
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.friendship import Friendship
from app.models.media import Media
from app.models.message import Message
from app.models.user import User
from app.models.watchlist import WatchlistItem

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "data")
USERS_FILE = "users.json"

# ── Media (from former seed_movies.py) ─────────────────────────────
CATALOG_FIELDS = (
    "title", "media_type", "description", "image_url", "year",
    "imdb_id", "rating", "votes", "imdb_url", "rank", "genres",
)
DETAIL_FIELDS = (
    "runtime_minutes", "episodes", "release_status",
    "director", "cast", "language", "country",
    "tagline", "awards", "trailer_url",
)
JSON_FIELD_MAP = {"status": "release_status"}
ALL_FIELDS = set(CATALOG_FIELDS) | set(DETAIL_FIELDS)

# ── Social seed (static graph + messages) ──────────────────────────
FRIENDSHIPS = [
    ("alice", "bob"),
    ("alice", "carol"),
    ("alice", "dave"),
    ("bob", "carol"),
    ("bob", "eve"),
    ("carol", "frank"),
    ("dave", "frank"),
    ("eve", "frank"),
]

MESSAGES = [
    ("alice", "bob",   "Hey! Have you watched #Breaking Bad? It's insane."),
    ("bob",   "alice", "Yeah! One of the best. #Inception is also up there for me."),
    ("alice", "bob",   "Totally! What are you watching now?"),
    ("bob",   "alice", "Just started #The Wire. Crime drama is my jam."),
    ("alice", "carol", "Carol! You HAVE to watch #Spirited Away 🌟"),
    ("carol", "alice", "Already seen it 5 times lol. #Your Name made me cry"),
    ("alice", "carol", "Sameee 😭 Let's do a watch party soon!"),
    ("bob",   "carol", "Anyone seen #Parasite? Blew my mind."),
    ("carol", "bob",   "Yes!! The twist 😱 Also #Oldboy if you like Korean cinema"),
    ("dave",  "frank", "Watched a great doc last night. #Planet Earth 2 is stunning."),
    ("frank", "dave",  "Nice. I'm more of an #Avengers guy haha"),
    ("dave",  "frank", "We are very different people 😂"),
    ("eve",   "frank", "Frank you need to watch #Get Out. Best horror in years."),
    ("frank", "eve",   "Horror isn't really my thing but I trust you!"),
    ("eve",   "frank", "Just watch it, seriously. #Hereditary too if you're brave enough"),
]


def load_media_json_files(media_type: str | None = None) -> list[dict]:
    """Load catalog JSON from app/data/, excluding users.json."""
    records: list[dict] = []
    pattern = os.path.join(DATA_DIR, "*.json")

    for filepath in sorted(glob.glob(pattern)):
        if os.path.basename(filepath) == USERS_FILE:
            continue
        with open(filepath, encoding="utf-8") as f:
            items = json.load(f)

        if not isinstance(items, list):
            continue

        for item in items:
            for old_key, new_key in JSON_FIELD_MAP.items():
                if old_key in item and new_key not in item:
                    item[new_key] = item.pop(old_key)

            if media_type and item.get("media_type") != media_type:
                continue
            records.append(item)

        basename = os.path.basename(filepath)
        type_counts: dict[str, int] = {}
        for item in items:
            t = item.get("media_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        print(f"  📂 {basename}: {len(items)} records {type_counts}")

    return records


def load_users_data() -> list[dict]:
    path = os.path.join(DATA_DIR, USERS_FILE)
    if not os.path.isfile(path):
        print(f"❌ Missing {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(f"❌ {USERS_FILE} must be a JSON array")
        sys.exit(1)
    return data


def seed_media(clear: bool = False, media_type: str | None = None) -> None:
    app = create_app()
    records = load_media_json_files(media_type=media_type)
    if not records:
        print("❌ No media records found in app/data/ (check *.json besides users.json)")
        sys.exit(1)

    with app.app_context():
        if clear:
            if media_type:
                deleted = Media.query.filter_by(media_type=media_type).delete()
            else:
                deleted = Media.query.delete()
            db.session.commit()
            print(f"🗑  Cleared {deleted} existing media rows.")

        added = 0
        updated = 0
        skipped = 0

        for record in records:
            imdb_id = record.get("imdb_id")
            if not imdb_id:
                skipped += 1
                continue

            media = Media.query.filter_by(imdb_id=imdb_id).first()

            if media:
                changed = False
                for field in ALL_FIELDS:
                    if field in record:
                        new_val = record[field]
                        if field == "media_type" and media.media_type == "anime" and new_val == "tvshow":
                            continue
                        if getattr(media, field, None) != new_val:
                            setattr(media, field, new_val)
                            changed = True
                if changed:
                    updated += 1
            else:
                kwargs: dict = {}
                for field in ALL_FIELDS:
                    if field in record:
                        kwargs[field] = record[field]

                if "title" not in kwargs:
                    skipped += 1
                    continue

                db.session.add(Media(**kwargs))
                added += 1

        db.session.commit()

        print(f"\n✅ Media seed complete")
        print(f"   Added:   {added}")
        print(f"   Updated: {updated}")
        print(f"   Skipped: {skipped}")
        print(f"\n📊 Database totals:")
        for t in ("movie", "anime", "tvshow"):
            count = Media.query.filter_by(media_type=t).count()
            if count:
                print(f"   {t}: {count}")
        print(f"   TOTAL: {Media.query.count()}")


def now_minus(minutes: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


def seed_users() -> None:
    users_data = load_users_data()
    app = create_app()

    with app.app_context():
        for u_data in users_data:
            existing = User.query.filter_by(username=u_data["username"]).first()
            if existing:
                WatchlistItem.query.filter_by(user_id=existing.id).delete()
                Friendship.query.filter(
                    (Friendship.requester_id == existing.id) | (Friendship.addressee_id == existing.id)
                ).delete()
                Message.query.filter(
                    (Message.sender_id == existing.id) | (Message.recipient_id == existing.id)
                ).delete()
                db.session.delete(existing)
        db.session.commit()

        user_map: dict[str, User] = {}
        for u_data in users_data:
            dob = u_data.get("date_of_birth")
            u = User(
                username=u_data["username"],
                email=u_data["email"],
                display_name=u_data["display_name"],
                bio=u_data["bio"],
                favorite_genres=u_data.get("favorite_genres") or u_data.get("genres", []),
                date_of_birth=date.fromisoformat(dob) if dob else None,
                profile_public=u_data.get("profile_public", True),
                allow_friend_requests=u_data.get("allow_friend_requests", True),
            )
            u.set_password(u_data["password"])
            db.session.add(u)
            db.session.flush()
            user_map[u_data["username"]] = u
            print(f"  ✓ User: {u_data['username']} (id={u.id})")

        db.session.commit()

        all_media = Media.query.all()
        if all_media:
            random.seed(42)
            statuses = ["watching", "planned", "completed"]
            for _username, user in user_map.items():
                sample = random.sample(all_media, min(20, len(all_media)))
                for i, media in enumerate(sample):
                    status = statuses[i % 3]
                    db.session.add(WatchlistItem(user_id=user.id, media_id=media.id, status=status))
            db.session.commit()
            print("  ✓ Watchlist items seeded")

        for req_name, addr_name in FRIENDSHIPS:
            req = user_map[req_name]
            addr = user_map[addr_name]
            db.session.add(
                Friendship(requester_id=req.id, addressee_id=addr.id, status="accepted")
            )
        db.session.commit()
        print(f"  ✓ {len(FRIENDSHIPS)} friendships created")

        for i, (sender_name, recipient_name, body) in enumerate(MESSAGES):
            sender = user_map[sender_name]
            recipient = user_map[recipient_name]
            db.session.add(
                Message(
                    sender_id=sender.id,
                    recipient_id=recipient.id,
                    body=body,
                    created_at=now_minus(len(MESSAGES) * 5 - i * 5),
                    read_at=now_minus(len(MESSAGES) * 5 - i * 5 - 1),
                )
            )
        db.session.commit()
        print(f"  ✓ {len(MESSAGES)} messages seeded")

        print("\n✅ Mock users ready!")
        print("\nCredentials (passwords as in app/data/users.json, default demo: Pass1234!)")
        print("-" * 40)
        for u_data in users_data:
            print(f"  {u_data['username']:10s}  {u_data['email']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed database from app/data/ (media JSON + users.json)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Wipe media table (or --type) before loading media; does not apply to --users-only",
    )
    parser.add_argument(
        "--type",
        choices=("movie", "anime", "tvshow"),
        help="Load only this media type",
    )
    parser.add_argument("--media-only", action="store_true", help="Only seed media")
    parser.add_argument("--users-only", action="store_true", help="Only seed users/social from users.json")
    args = parser.parse_args()

    if args.media_only and args.users_only:
        print("❌ Use only one of --media-only or --users-only")
        sys.exit(1)

    if args.users_only:
        seed_users()
        return

    seed_media(clear=args.clear, media_type=args.type)

    if not args.media_only:
        print("\n" + "=" * 60)
        print("Seeding users from app/data/users.json …")
        print("=" * 60)
        seed_users()


if __name__ == "__main__":
    main()

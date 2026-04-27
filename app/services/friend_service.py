# -*- coding: utf-8 -*-
from sqlalchemy import or_, and_
from app.extensions import db
from app.models.friendship import Friendship
from app.models.user import User


def send_request(requester_id, addressee_id):
    if requester_id == addressee_id:
        return None, "Cannot send a friend request to yourself"
    target = db.session.get(User, addressee_id)
    if not target:
        return None, "User not found"
    if not target.allow_friend_requests:
        return None, "This user is not accepting friend requests"
    existing = Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == requester_id, Friendship.addressee_id == addressee_id),
            and_(Friendship.requester_id == addressee_id, Friendship.addressee_id == requester_id),
        )
    ).first()
    if existing:
        if existing.status == "accepted":
            return None, "Already friends"
        if existing.status == "pending":
            return None, "Friend request already pending"
        # rejected — allow re-send by updating
        existing.status = "pending"
        existing.requester_id = requester_id
        existing.addressee_id = addressee_id
        db.session.commit()
        return existing, None
    fs = Friendship(requester_id=requester_id, addressee_id=addressee_id)
    db.session.add(fs)
    db.session.commit()
    return fs, None


def respond_to_request(friendship_id, user_id, action):
    fs = db.session.get(Friendship, friendship_id)
    if not fs:
        return None, "Request not found"
    if fs.addressee_id != user_id:
        return None, "Not authorised"
    if fs.status != "pending":
        return None, "Request already resolved"
    if action == "accept":
        fs.status = "accepted"
    elif action == "reject":
        fs.status = "rejected"
    else:
        return None, "Invalid action"
    db.session.commit()
    return fs, None


def remove_friend(friendship_id, user_id):
    fs = db.session.get(Friendship, friendship_id)
    if not fs:
        return False, "Friendship not found"
    if fs.requester_id != user_id and fs.addressee_id != user_id:
        return False, "Not authorised"
    db.session.delete(fs)
    db.session.commit()
    return True, None


def get_friends(user_id):
    rows = Friendship.query.filter(
        or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
        Friendship.status == "accepted",
    ).all()
    result = []
    for fs in rows:
        friend_id = fs.addressee_id if fs.requester_id == user_id else fs.requester_id
        u = db.session.get(User, friend_id)
        if u:
            d = u.to_public_dict()
            d["friendship_id"] = fs.id
            result.append(d)
    return result


def get_pending_received(user_id):
    return Friendship.query.filter_by(addressee_id=user_id, status="pending").all()


def get_pending_sent(user_id):
    return Friendship.query.filter_by(requester_id=user_id, status="pending").all()


def are_friends(user_id_a, user_id_b):
    return Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == user_id_a, Friendship.addressee_id == user_id_b),
            and_(Friendship.requester_id == user_id_b, Friendship.addressee_id == user_id_a),
        ),
        Friendship.status == "accepted",
    ).first() is not None


def get_friendship(user_id_a, user_id_b):
    return Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == user_id_a, Friendship.addressee_id == user_id_b),
            and_(Friendship.requester_id == user_id_b, Friendship.addressee_id == user_id_a),
        )
    ).first()

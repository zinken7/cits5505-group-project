# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from app.extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    read_at = db.Column(db.DateTime, nullable=True)

    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = db.relationship("User", foreign_keys=[recipient_id], backref="received_messages")

    __table_args__ = (
        db.Index("ix_messages_conv", "sender_id", "recipient_id"),
        db.Index("ix_messages_conv_rev", "recipient_id", "sender_id"),
    )

    def to_dict(self, tags=None):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "sender_username": self.sender.username if self.sender else None,
            "recipient_id": self.recipient_id,
            "body": self.body,
            "tags": tags or [],
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None,
            "read_at": self.read_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.read_at else None,
        }

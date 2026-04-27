# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from app.extensions import db


class Friendship(db.Model):
    __tablename__ = "friendships"

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    addressee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | accepted | rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    requester = db.relationship("User", foreign_keys=[requester_id], backref="sent_requests")
    addressee = db.relationship("User", foreign_keys=[addressee_id], backref="received_requests")

    __table_args__ = (
        db.UniqueConstraint("requester_id", "addressee_id", name="uq_friendship"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "requester": self.requester.to_public_dict() if self.requester else None,
            "addressee": self.addressee.to_public_dict() if self.addressee else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

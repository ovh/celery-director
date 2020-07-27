import enum
import uuid

from sqlalchemy_utils import UUIDType

from director.extensions import db


def get_uuid():
    return str(uuid.uuid4())


class StatusType(enum.Enum):
    pending = "pending"
    progress = "progress"
    success = "success"
    error = "error"
    canceled = "canceled"


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(
        UUIDType(binary=False), primary_key=True, nullable=False, default=get_uuid
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=db.func.now(), nullable=False, index=True
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    def commit(self):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def save(self):
        db.session.add(self)
        self.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "created": self.created_at.isoformat(),
            "updated": self.updated_at.isoformat(),
        }

import json

from sqlalchemy_utils import UUIDType
from sqlalchemy.types import PickleType

from director.extensions import db
from director.exceptions import UserNotFound
from director.models import BaseModel, StatusType
from director.models.utils import JSONBType


class User(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def update(self):
        user = self.query.filter_by(username=self.username).first()
        if not user:
            raise UserNotFound(f"User {self.username} not found")

        user.password = self.password

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def delete(self):
        db.session.delete(self)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def to_dict(self):
        d = super().to_dict()
        d.update({"username": self.username, "password": self.password})
        return d

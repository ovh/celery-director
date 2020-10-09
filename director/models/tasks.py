import json

from sqlalchemy_utils import UUIDType
from sqlalchemy.types import PickleType

from director.extensions import db
from director.models import BaseModel, StatusType
from director.models.utils import JSONBType


class Task(BaseModel):
    __tablename__ = "tasks"

    key = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(StatusType), default=StatusType.pending, nullable=False)
    previous = db.Column(JSONBType, default=[])
    result = db.Column(PickleType)

    # Relationship
    workflow_id = db.Column(
        UUIDType(binary=False),
        db.ForeignKey("workflows.id"),
        nullable=False,
        index=True,
    )
    workflow = db.relationship("Workflow", backref=db.backref("tasks", lazy=True))

    def __repr__(self):
        return f"<Task {self.key}>"

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {
                "key": self.key,
                "status": self.status.value,
                "task": self.id,
                "previous": self.previous,
                "result": self.result,
            }
        )
        return d

from director.extensions import db
from director.models import BaseModel, StatusType
from director.models.utils import JSONBType
from sqlalchemy_utils import UUIDType


class Workflow(BaseModel):
    __tablename__ = "workflows"

    name = db.Column(db.String(255), nullable=False)
    project = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(StatusType), default=StatusType.pending, nullable=False)
    payload = db.Column(JSONBType, default={})
    periodic = db.Column(db.Boolean, default=False)

    # Relationship
    # parent_id = db.Column(
    #     UUIDType(binary=False),
    #     db.ForeignKey("workflows.id"),
    #     nullable=True,
    #     index=True,
    # )
    # workflow = db.relationship("Workflow", remote_side=[parent_id])

    def __str__(self):
        return f"{self.project}.{self.name}"

    def __repr__(self):
        return f"<Workflow {self.project}.{self.name}>"

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {
                "name": self.name,
                "payload": self.payload,
                "project": self.project,
                "fullname": f"{self.project}.{self.name}",
                "status": self.status.value,
                "periodic": self.periodic,
            }
        )
        return d

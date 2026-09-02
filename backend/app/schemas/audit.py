from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    actor_type: str
    actor_id: str
    event_type: str
    entity_type: str
    entity_id: str
    detail: str
    created_at: datetime

    model_config = {"from_attributes": True}


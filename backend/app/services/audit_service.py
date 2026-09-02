from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog


def write_audit_log(
    db: Session,
    merchant_id: int,
    event_type: str,
    entity_type: str,
    entity_id: str,
    detail: str,
    actor_type: str = "merchant",
    actor_id: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        merchant_id=merchant_id,
        actor_type=actor_type,
        actor_id=actor_id or str(merchant_id),
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail,
    )
    db.add(entry)
    return entry


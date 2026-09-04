from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import audit, auth, catalog, dashboard, decision_center, recommendations, shopping, webhooks
import app.db.models  # noqa: F401 - imports every ORM model before metadata creation
from app.core.config import get_frontend_origins
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.scripts.seed_demo_data import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title="Arvya Growth Agent API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(catalog.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(decision_center.router, prefix="/api/v1")
app.include_router(shopping.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "arvya-growth-agent-api"}

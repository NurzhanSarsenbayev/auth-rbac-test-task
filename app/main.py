from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.auth import router as auth_router
from app.api.users import router as users_router

from app.core.config import settings
from app.db.session import get_db


app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(users_router)

@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def db_healthcheck(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
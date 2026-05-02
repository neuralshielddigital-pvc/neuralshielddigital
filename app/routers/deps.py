from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db


def get_database(db: Session = Depends(get_db)) -> Session:
    return db


from fastapi import Request, HTTPException, status

from fastapi import Request
from fastapi.responses import RedirectResponse

def require_admin(request: Request):
    admin = request.session.get("admin")

    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    return admin

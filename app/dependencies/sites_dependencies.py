from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.site_service import SiteService


def get_site_service(db: Session = Depends(get_db)) -> SiteService:
    return SiteService(db)
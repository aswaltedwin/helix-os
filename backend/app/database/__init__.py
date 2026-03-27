from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.database.base import Base

def init_db():
    from app.database import models
    Base.metadata.create_all(bind=engine)
    
    # Seed default organization if it doesn't exist
    db = SessionLocal()
    try:
        org_id = "org-demo"
        org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
        if not org:
            org = models.Organization(
                id=org_id,
                name="Demo Organization",
                industry="Technology"
            )
            db.add(org)
            db.commit()
    finally:
        db.close()


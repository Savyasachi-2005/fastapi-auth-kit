from sqlalchemy.orm import Session
from app.models.roles import Role

def get_by_name(db:Session,name:str):
    return db.query(Role).filter(Role.name==name).first()

def create(db:Session,*,name:str,description:str|None=None)->Role:
    role=Role(name=name,description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
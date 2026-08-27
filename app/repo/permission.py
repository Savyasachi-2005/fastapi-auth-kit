from sqlalchemy.orm import Session

from app.models.permission import Permission

def get_by_code(db:Session,code:str)->Permission|None:
    return db.query(Permission).filter(Permission.code==code).first()

def  create(db:Session,*,code:str,description:str|None=None)->Permission:
    perm=Permission(code=code,description=description)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


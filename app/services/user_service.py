from sqlalchemy.orm import Session
from app.crud import crud

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload):
        return crud.create_user(self.db, payload)

    def list(self, skip=0, limit=25, role=None):
        return crud.list_users(self.db, skip=skip, limit=limit, role=role)

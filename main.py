from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any

app = FastAPI()

# Configuración de CORS para permitir todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

DATABASE_URL = "mysql+mysqlconnector://user:password@host:port/database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    birth = Column(Integer)
    highest = Column(Integer)
    match = Column(Integer)
    rank = Column(Integer)
    rating = Column(Integer)
    user = Column(String(255))
    win = Column(Integer)


Base.metadata.create_all(bind=engine)


class User(BaseModel):
    birth: int
    highest: int
    id: int
    match: int
    rank: int
    rating: int
    user: str
    win: int


class MySQLAPI:
    def __init__(self):
        self.db = SessionLocal()

    def read(self) -> List[Dict[str, Any]]:
        users = self.db.query(UserModel).all()
        return [user.__dict__ for user in users]

    def write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        new_user = UserModel(**data)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return {"Status": "Successfully Inserted", "User_ID": new_user.id}

    def update(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return {"Status": "User not found"}
        for key, value in data.items():
            setattr(user, key, value)
        self.db.commit()
        return {"Status": "Successfully Updated"}

    def delete(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return {"Status": "User not found"}
        self.db.delete(user)
        self.db.commit()
        return {"Status": "Successfully Deleted"}


@app.get("/")
async def base():
    return {"Status": "UP"}


@app.get("/mysql", response_model=List[User])
async def mysql_read():
    db = MySQLAPI()
    response = db.read()
    return response


@app.post("/mysql", response_model=Dict[str, Any])
async def mysql_write(user: User):
    db = MySQLAPI()
    response = db.write(user.dict())
    return response


@app.put("/mysql/{user_id}", response_model=Dict[str, Any])
async def mysql_update(user_id: int, user: User):
    db = MySQLAPI()
    response = db.update(user_id, user.dict())
    return response


@app.delete("/mysql/{user_id}", response_model=Dict[str, Any])
async def mysql_delete(user_id: int):
    db = MySQLAPI()
    response = db.delete(user_id)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

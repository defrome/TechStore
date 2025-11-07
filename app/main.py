from database import db
from database.db import Base, engine, SessionLocal, User
from database import *
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse, FileResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create_user")
def create_user(
        first_name: str = "Alexander",
        surname: str = "Ivanov",
        status: str = "active",
        balance: float = 10000,
        is_premium: bool = True,
        number_of_orders: int = 10,
        db: Session = Depends(get_db)
):
    try:
        new_user = User(
            first_name=first_name,
            surname=surname,
            status=status,
            balance=balance,
            is_premium=is_premium,
            number_of_orders=number_of_orders
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created successfully",
            "user_id": new_user.id,
            "first_name": new_user.first_name,
            "surname": new_user.surname
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

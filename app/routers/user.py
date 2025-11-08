from fastapi import APIRouter, Depends, HTTPException, status
from app.database.db import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.models import User

router = APIRouter()

@router.get("/get_users")
async def get_users(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()

        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "first_name": user.first_name,
                "surname": user.surname,
                "status": user.status,
                "balance": user.balance,
                "is_premium": user.is_premium,
                "number_of_orders": user.number_of_orders
            })

        return {"users": user_list}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users: {str(e)}"
        )


@router.post("/create_user")
async def create_user(first_name: str = "Alexander",
                      surname: str = "Ivanov",
                      status: str = "active",
                      balance: float = 10000,
                      is_premium: bool = True,
                      number_of_orders: int = 10,
                      db: AsyncSession = Depends(get_db)):
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
        await db.commit()
        await db.refresh(new_user)

        return {
            "message": "User created successfully",
            "user_id": new_user.id
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
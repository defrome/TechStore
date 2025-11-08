from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.database.db import AsyncSession
from app.database.db import get_db
from app.models.models import User, Item

router = APIRouter()

@router.get("/get_item")
async def get_items(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Item))
        items = result.scalars().all()

        item_list = []
        for item in items:
            item_list.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "availability_status": item.availability_status,
                "manufacturer": item.manufacturer,
                "quantity": item.quantity,
            })

        return {"users": item_list}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting item: {str(e)}"
        )



@router.post("/create_item")
async def create_item(name: str = "IPhone 17 Pro",
                      description: str = "Test Description",
                      availability_status: str = "Available",
                      manufacturer: str = "Apple",
                      quantity: int = 34,
                      db: AsyncSession = Depends(get_db)):
    try:
        new_item = Item(
            name=name,
            description=description,
            availability_status=availability_status,
            manufacturer=manufacturer,
            quantity=quantity
        )

        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)

        return {
            "message": "Item created successfully",
            "user_id": new_item.id
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
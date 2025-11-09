from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, delete

from app.database.db import AsyncSession
from app.database.db import get_db
from app.models.models import User, Item, Category, item_category

router = APIRouter()

@router.get("/get_item")
async def get_items(
        db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Item))
        items = result.scalars().all()

        item_list = []
        for item in items:
            categories_result = await db.execute(
                select(Category)
                .join(item_category)
                .where(item_category.c.item_id == item.id)
            )
            categories = categories_result.scalars().all()

            item_list.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "availability_status": item.availability_status,
                "manufacturer": item.manufacturer,
                "quantity": item.quantity,
                "image": item.image,
                "categories": [
                    {
                        "id": cat.id,
                        "name": cat.name,
                        "description": cat.description
                    } for cat in categories
                ]
            })

        return {"items": item_list}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting items: {str(e)}"
        )



@router.post("/create_item")
async def create_item(name: str = "IPhone 17 Pro",
                      description: str = "Test Description",
                      price: int = 50000,
                      availability_status: bool = True,
                      manufacturer: str = "Apple",
                      quantity: int = 34,
                      image: str = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fiphoriya.ru%2Fproduct%2Fapple-iphone-17-pro-1tb-deep-blue&psig=AOvVaw2G9RtQjWq92Ld867O7Z5tn&ust=1762680640661000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCPD9lJ2f4pADFQAAAAAdAAAAABAE",
                      db: AsyncSession = Depends(get_db)):
    try:
        new_item = Item(
            name=name,
            description=description,
            price=price,
            availability_status=availability_status,
            manufacturer=manufacturer,
            quantity=quantity,
            image=image
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


@router.delete("/delete_items")
async def delete_item_by_id(
        item_id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            delete(Item).where(Item.id == item_id)
        )
        await db.commit()

        if result.rowcount > 0:
            return {"message": f"Item {item_id} deleted successfully"}
        else:
            return {"message": f"Item {item_id} not found"}

    except Exception as e:
        await db.rollback()
        raise e
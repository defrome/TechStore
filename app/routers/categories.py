from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, insert

from app.database.db import AsyncSession
from app.database.db import get_db
from app.models.models import User, Item, Category, item_category

router = APIRouter()



@router.post("/add_item_to_categories")
async def add_item_to_categories(
        item_id: int,
        category_ids: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        item = await db.get(Item, item_id)
        if not item:
            raise HTTPException(404, "Item not found")

        category_id_list = [int(id.strip()) for id in category_ids.split(",") if id.strip().isdigit()]

        if not category_id_list:
            raise HTTPException(400, "No valid category IDs provided")

        added_categories = []
        skipped_categories = []

        for category_id in category_id_list:
            category = await db.get(Category, category_id)
            if not category:
                skipped_categories.append(f"Category {category_id} not found")
                continue

            existing = await db.execute(
                select(item_category).where(
                    item_category.c.item_id == item_id,
                    item_category.c.category_id == category_id
                )
            )
            if existing.first():
                skipped_categories.append(f"Already in category '{category.name}'")
                continue

            await db.execute(
                item_category.insert().values(
                    item_id=item_id,
                    category_id=category_id
                )
            )
            added_categories.append(category.name)

        await db.commit()

        return {
            "message": f"Item '{item.name}' category associations updated",
            "added_to_categories": added_categories,
            "skipped_categories": skipped_categories
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Error: {str(e)}")



@router.post("/create_categories")
async def create_category(
    name: str = "Apple",
    description: str = "Test",
    db: AsyncSession = Depends(get_db)
):
    try:
        existing_category = await db.execute(
            select(Category).where(Category.name == name)
        )
        if existing_category.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

        new_category = Category(
            name=name,
            description=description
        )

        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

        return {
            "message": "Category created successfully",
            "category_id": new_category.id,
            "name": new_category.name,
            "description": new_category.description
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )
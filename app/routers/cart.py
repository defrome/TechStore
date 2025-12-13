from fastapi import APIRouter, Depends, HTTPException, status
from app.database.db import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.models import Cart, Item

router = APIRouter()

@router.get("/get_cart")
async def get_user_cart(cart_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Cart).where(Cart.id == cart_id)
        )
        cart_items = result.scalars().all()

        cart = []
        for cart_item in cart_items:
            item_result = await db.execute(
                select(Item).where(Item.id == cart_item.item_id)
            )
            item = item_result.scalar_one_or_none()

            if item:
                cart.append({
                    "item_id": item.id,
                    "item_name": item.name,
                    "item_price": item.price,
                    "item_image": item.image,
                    "quantity": cart_item.item_value,
                    "total_price": item.price * cart_item.item_value
                })

        total_cart_price = sum(item["total_price"] for item in cart)

        return {
            "cart_id": cart_id,
            "cart_items": cart,
            "total_cart_price": total_cart_price,
            "total_items": len(cart)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user cart: {str(e)}"
        )

@router.delete("/remove_item_from_cart")
async def remove_item_from_cart(
    user_id: str,
    item_id: int,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    try:

        result = await db.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.item_id == item_id
            )
        )
        cart_item = result.scalar_one_or_none()

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart"
            )


        if quantity > cart_item.item_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove {quantity} items. Only {cart_item.item_value} in cart"
            )


        if quantity == cart_item.item_value:

            await db.delete(cart_item)
            action = "completely removed"
            remaining_quantity = 0
        else:

            cart_item.item_value -= quantity
            action = f"quantity decreased by {quantity}"
            remaining_quantity = cart_item.item_value

        await db.commit()

        return {
            "message": f"Item {action} from cart successfully",
            "user_id": user_id,
            "item_id": item_id,
            "removed_quantity": quantity,
            "remaining_quantity": remaining_quantity,
            "action": action
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing item from cart: {str(e)}"
        )

@router.post("/cart_add_item")
async def add_item(
    cart_id: int,
    item_id: int,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    try:

        result = await db.execute(
            select(Cart).where(
                Cart.id == cart_id,
                Cart.item_id == item_id
            )
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:

            cart_item.item_value += quantity
            action = "quantity increased"
            new_quantity = cart_item.item_value
        else:

            cart_item = Cart(
                cart_id=cart_id,
                item_id=item_id,
                item_value=quantity
            )
            db.add(cart_item)
            action = "new item added"
            new_quantity = quantity

        await db.commit()

        return {
            "message": f"Item {action} to cart successfully",
            "cart_id": cart_id,
            "item_id": item_id,
            "added_quantity": quantity,
            "new_quantity": new_quantity,
            "action": action
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding item to cart: {str(e)}"
        )

@router.post("/create_cart")
async def create_cart(
                      item_id: int,
                      value: int = 1,
                      db: AsyncSession = Depends(get_db)):
    try:
        new_cart = Cart(
            item_id=item_id,
            item_value=value
        )

        db.add(new_cart)
        await db.commit()
        await db.refresh(new_cart)

        return {
            "message": "Cart created successfully",
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

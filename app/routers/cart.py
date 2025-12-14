from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database.db import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.models import Cart, Item

router = APIRouter()

@router.get("/get_cart")
async def get_user_cart(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    session_id = request.state.session_id

    try:
        result = await db.execute(
            select(Cart).where(Cart.session_id == session_id)
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

        total_cart_price = sum(i["total_price"] for i in cart)

        return {
            "session_id": session_id,
            "cart_items": cart,
            "total_cart_price": total_cart_price,
            "total_items": len(cart)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user cart: {str(e)}"
        )


@router.delete("/remove_item_from_cart")
async def remove_item_from_cart(
    request: Request,
    item_id: int,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    session_id = request.state.session_id

    try:
        result = await db.execute(
            select(Cart).where(
                Cart.session_id == session_id,
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
                detail=f"Cannot remove {quantity}. Only {cart_item.item_value} in cart"
            )

        if quantity == cart_item.item_value:
            await db.delete(cart_item)
            remaining_quantity = 0
            action = "completely removed"
        else:
            cart_item.item_value -= quantity
            remaining_quantity = cart_item.item_value
            action = f"quantity decreased by {quantity}"

        await db.commit()

        return {
            "message": f"Item {action} successfully",
            "session_id": session_id,
            "item_id": item_id,
            "remaining_quantity": remaining_quantity
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing item from cart: {str(e)}"
        )


@router.post("/cart/add")
async def add_item(
    request: Request,
    item_id: int,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    session_id = request.state.session_id

    try:
        result = await db.execute(
            select(Cart).where(
                Cart.session_id == session_id,
                Cart.item_id == item_id
            )
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:
            cart_item.item_value += quantity
            new_quantity = cart_item.item_value
            action = "quantity increased"
        else:
            cart_item = Cart(
                session_id=session_id,
                item_id=item_id,
                item_value=quantity
            )
            db.add(cart_item)
            new_quantity = quantity
            action = "new item added"

        await db.commit()

        return {
            "message": f"Item {action} successfully",
            "session_id": session_id,
            "item_id": item_id,
            "quantity": new_quantity
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding item to cart: {str(e)}"
        )


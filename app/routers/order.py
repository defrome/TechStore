from fastapi import APIRouter, Depends, HTTPException, status
from app.database.db import AsyncSession
from sqlalchemy import select, delete
from app.database.db import get_db
from app.models.models import Order, Cart, OrderItem, Item

router = APIRouter()


@router.post("/create_order", status_code=status.HTTP_201_CREATED)
async def create_order(
        cart_id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        cart_result = await db.execute(
            select(Cart).where(Cart.id == cart_id)
        )
        cart_items = cart_result.scalars().all()

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )

        item_ids = [cart_item.item_id for cart_item in cart_items]
        items_result = await db.execute(
            select(Item).where(Item.id.in_(item_ids))
        )
        items = {item.id: item for item in items_result.scalars().all()}

        unavailable_items = []
        for cart_item in cart_items:
            item = items.get(cart_item.item_id)
            if not item:
                unavailable_items.append(f"Item {cart_item.item_id} not found")
                continue
            if not item.availability_status:
                unavailable_items.append(f"Item '{item.name}' is not available")
                continue
            if item.quantity < cart_item.item_value:
                unavailable_items.append(
                    f"Not enough stock for '{item.name}'. Available: {item.quantity}, requested: {cart_item.item_value}"
                )

        if unavailable_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"unavailable_items": unavailable_items}
            )

        new_order = Order(
            cart_id=cart_id,
            total_amount=0,
            total_items=0
        )

        db.add(new_order)
        await db.flush()

        total_amount = 0
        total_items = 0
        order_items_list = []

        for cart_item in cart_items:
            item = items[cart_item.item_id]

            order_item = OrderItem(
                order_id=new_order.id,
                item_id=item.id,
                quantity=cart_item.item_value,
                price_at_time=item.price
            )
            db.add(order_item)

            item.quantity -= cart_item.item_value

            subtotal = item.price * cart_item.item_value
            total_amount += subtotal
            total_items += cart_item.item_value

            order_items_list.append({
                "item_id": item.id,
                "name": item.name,
                "quantity": cart_item.item_value,
                "price": item.price,
                "subtotal": subtotal
            })

        new_order.total_amount = total_amount
        new_order.total_items = total_items

        await db.execute(
            delete(Cart).where(Cart.id == cart_id)
        )

        await db.commit()
        await db.refresh(new_order)

        return {
            "message": "Order created successfully",
            "order_id": new_order.id,
            "cart_id": cart_id,
            "total_amount": total_amount,
            "total_items": total_items,
            "items": order_items_list,
            "created_at": new_order.created_at.isoformat() if new_order.created_at else None
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )
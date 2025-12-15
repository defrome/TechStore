import random
import string
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import TEST_LOGIN, TEST_PASSWORD
from app.database.db import get_db
from app.models.models import Admin, Order
import secrets

router = APIRouter()

security = HTTPBasic()

async def verify_admin(
        credentials: HTTPBasicCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> Admin:

    if (credentials.username == TEST_LOGIN and
            credentials.password == TEST_PASSWORD):

        return Admin(
            id=0,
            username=TEST_LOGIN,
            password=TEST_PASSWORD,
            login=TEST_LOGIN,
            status=True
        )

    stmt = select(Admin).where(
        Admin.login == credentials.username
    ).where(Admin.status == True)

    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()

    if not admin:
        secrets.compare_digest(credentials.password, "dummy_password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not secrets.compare_digest(credentials.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )

    return admin

def generate_password(length=12, use_digits=True, use_special=True):

    if length < 4:
        length = 4

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits if use_digits else ''
    special = '!@#$%^&*()_+-=[]{}|;:,.<>?' if use_special else ''

    all_chars = lowercase + uppercase + digits + special

    if not all_chars:
        return ""

    password_chars = []

    password_chars.append(random.choice(lowercase))
    password_chars.append(random.choice(uppercase))

    if use_digits:
        password_chars.append(random.choice(digits))

    if use_special:
        password_chars.append(random.choice(special))

    for _ in range(length - len(password_chars)):
        password_chars.append(random.choice(all_chars))

    random.shuffle(password_chars)

    return ''.join(password_chars)

@router.get("/admin/dashboard")
async def admin_dashboard(username: str = Depends(verify_admin)):
    return {"message": f"Welcome admin {username}"}

@router.post("/create_admin")
async def create_admin(
        db: AsyncSession = Depends(get_db),
        username: str = "admin",
        auth: str = Depends(verify_admin)
):
    try:
        new_admin = Admin(
            username=username,
            password=generate_password(16),
            login=generate_password(10),
        )

        db.add(new_admin)
        await db.commit()
        await db.refresh(new_admin)

        return {
            "result": "Admin succesful created",
            "admin_id": new_admin.id,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin: {str(e)}"
        )

@router.get("/get_admins")
async def get_admins(
        db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Admin))
        admins = result.scalars().all()

        admin_list = []
        for a in admins:
            admin_list.append({
                "id": a.id,
                "status": a.status,
            })

        return {"result": admin_list}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admins: {str(e)}"
        )

@router.get("/admin_orders")
async def get_admin_routers(db: AsyncSession = Depends(get_db),
                            auth: str = Depends(verify_admin)):
    try:
        result = await db.execute(select(Order))
        orders = result.scalars().all()

        order_list = []

        for order in orders:
            order_list.append({
                "id": order.id,
                "total_amount": order.total_amount,
                "total_items": order.total_items,
                "status": order.status,
                "created_at": order.created_at
            })

        return {"orders": order_list}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error get orders: {str(e)}"
        )

@router.post("/accept_order")
async def accept_order(
    order_id: int,  # FastAPI автоматически конвертирует
    db: AsyncSession = Depends(get_db),
    auth: str = Depends(verify_admin)
):
    try:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )

        order.status = "accepted"
        await db.commit()
        await db.refresh(order)

        return {
            "message": f"Order {order_id} accepted successfully",
            "order_id": order.id,
            "new_status": order.status
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accepting order: {str(e)}"
        )

@router.post("/reject_order")
async def reject_order(
    order_id: int,  # FastAPI автоматически конвертирует
    db: AsyncSession = Depends(get_db),
    auth: str = Depends(verify_admin)
):
    try:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )

        order.status = "rejected"
        await db.commit()
        await db.refresh(order)

        return {
            "message": f"Order {order_id} accepted successfully",
            "order_id": order.id,
            "new_status": order.status
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accepting order: {str(e)}"
        )

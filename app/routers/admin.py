import random
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.database.db import get_db
from app.models.models import Admin

router = APIRouter()

def generate_password(length=12, use_digits=True, use_special=True):

    if length < 4:
        length = 4

    lowercase = string.ascii_lowercase  # a-z
    uppercase = string.ascii_uppercase  # A-Z
    digits = string.digits if use_digits else ''  # 0-9
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


@router.post("/create_admin")
async def create_admin(
        db: AsyncSession = Depends(get_db)
):
    try:
        new_admin = Admin(
            password=generate_password(16),
            login=generate_password(10),
        )

        db.add(new_admin)
        await db.commit()
        await db.refresh(new_admin)

        return {
            "result": "Admin succesful created",
            "admin_id": new_admin.id
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin: {str(e)}"
        )

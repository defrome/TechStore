# app/middlewares/create_session.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from datetime import datetime, timedelta


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Проверяем, есть ли session_id в cookies
        session_id = request.cookies.get("session_id")

        if not session_id:
            # Создаем новый session_id
            session_id = str(uuid.uuid4())
            print(f"NEW SESSION CREATED: {session_id}")

        # Сохраняем session_id в state
        request.state.session_id = session_id

        # Получаем response
        response = await call_next(request)

        # Устанавливаем cookie если ее не было
        if not request.cookies.get("session_id"):
            response.set_cookie(
                key="session_id",
                value=session_id,
                max_age=86400,  # 1 день
                httponly=True,
                samesite="lax"
            )
            print(f"SET COOKIE: {session_id}")

        return response
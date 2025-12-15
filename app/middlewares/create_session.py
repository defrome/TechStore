# app/middlewares/create_session.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from datetime import datetime, timedelta


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        session_id = request.cookies.get("session_id")

        if not session_id:

            session_id = str(uuid.uuid4())
            print(f"NEW SESSION CREATED: {session_id}")

        request.state.session_id = session_id

        response = await call_next(request)

        if not request.cookies.get("session_id"):
            response.set_cookie(
                key="session_id",
                value=session_id,
                max_age=86400,
                httponly=True,
                samesite="lax"
            )
            print(f"SET COOKIE: {session_id}")

        return response
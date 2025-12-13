from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get("session_id")

        if not session_id:
            session_id = str(uuid4())
            request.state.session_id = session_id
            response = await call_next(request)
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                samesite="lax"
            )
            return response

        request.state.session_id = session_id
        return await call_next(request)

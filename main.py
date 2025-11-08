from app.database.db import Base, engine
from fastapi import FastAPI
from app.routers import user
import asyncio

app = FastAPI()

app.include_router(user.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
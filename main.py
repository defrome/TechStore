from fastapi.middleware.cors import CORSMiddleware

from app.database.db import Base, engine
from fastapi import FastAPI
from app.routers import user, items, categories
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(items.router)
app.include_router(categories.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
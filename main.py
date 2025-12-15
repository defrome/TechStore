from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.admin.categories_admin import CategoryAdmin
from app.admin.items_admin import ItemAdmin
from app.database.db import Base, engine
from fastapi import FastAPI
from app.middlewares.create_session import SessionMiddleware
from app.routers import items, categories, cart, order
from app.routers import admin as adm


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)



app = FastAPI(lifespan=lifespan)

admin = Admin(
    app,
    engine,
    title="My Admin",
    base_url="/api/admin",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все origin (не для production!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(adm.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(order.router)

admin.add_view(ItemAdmin)
admin.add_view(CategoryAdmin)

app.add_middleware(SessionMiddleware)

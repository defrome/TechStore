from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.admin.categories_admin import CategoryAdmin
from app.admin.items_admin import ItemAdmin
from app.admin.users_admin import UserAdmin
from app.database.db import Base, engine
from fastapi import FastAPI
from app.routers import user, items, categories, cart


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(items.router)
app.include_router(categories.router)
app.include_router(cart.router)

admin.add_view(ItemAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(UserAdmin)
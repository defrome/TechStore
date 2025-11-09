from sqladmin import ModelView

from app.models.models import Category


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id,
                   Category.name,
                   Category.description]
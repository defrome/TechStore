from sqladmin import ModelView

from app.models.models import Item


class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id,
                   Item.name,
                   Item.description,
                   Item.price,
                   Item.availability_status,
                   Item.manufacturer,
                   Item.quantity,
                   Item.image,
                   Item.categories]

    form_include_pk = True
    form_columns = [
        Item.name,
        Item.description,
        Item.price,
        Item.availability_status,
        Item.manufacturer,
        Item.quantity,
        Item.image,
        Item.categories
    ]

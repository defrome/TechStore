from sqladmin import ModelView

from app.models.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id,
                   User.first_name,
                   User.surname,
                   User.status,
                   User.balance,
                   User.is_premium,
                   User.number_of_orders,
                   User.avatar_image
                   ]
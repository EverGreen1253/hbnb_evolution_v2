from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        # Note that the attribute has an underscore. It seems that getters don't work??
        return super().get_by_attribute("_email", email)

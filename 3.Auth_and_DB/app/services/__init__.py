from app.services.facade import HBnBFacade
from app.persistence.repository import InMemoryRepository
from app.persistence.user_repository import UserRepository

facade = HBnBFacade()
admin_details = {
    "first_name": "Super",
    "last_name": "Admin",
    "email": "super.admin@hbnb.com",
    "password": "password",
    "is_admin": True
}

# Task 4 - create a default admin user to overcome the chicken-and-egg problem
# that will happen when the Create User has a @jwt_required slapped on top of it.
# Check to ensure that we are still using InMemoryRepository or there will be an error

if isinstance(facade.user_repo, InMemoryRepository):
    facade.create_user(admin_details)

# Task 6 - Same as before, except we need to check the DB first to ensure that there 
# isn't already a Super Admin inside. Unlike the InMemoryRepo, the data in the DB
# will persist across sessions.

if isinstance(facade.user_repo, UserRepository):
    result = facade.user_repo.get_user_by_email("super.admin@hbnb.com")

    # If no Super Admin exists, create a new one
    if result is None:
        facade.create_user(admin_details)
    # else:
    #     print('Super Admin user already exists. Moving on...')

# With this default admin, we now will be able to log into the system to create more users.
# curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" -H "Content-Type: application/json" -d '{ "email": "super.admin@hbnb.com", "password": "password" }'

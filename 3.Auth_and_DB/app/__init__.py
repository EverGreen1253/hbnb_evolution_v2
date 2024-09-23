""" Constructor for the 'app' module """
from app.services.facade import HBnBFacade

facade = HBnBFacade()

# Task 4 - create a default admin user to overcome the chicken-and-egg problem
# that will happen when the Create User has a @jwt_required slapped on top of it.

facade.create_user({
    "first_name": "Super",
    "last_name": "Admin",
    "email": "super.admin@hbnb.com",
    "password": "password",
    "is_admin": True
})

# With this default admin, we now will be able to log into the system to create more users.
# curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" -H "Content-Type: application/json" -d '{ "email": "super.admin@hbnb.com", "password": "password" }'

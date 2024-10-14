""" Constructor for the 'app' module """
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
from app.api.v1.protected import api as protected_ns
from flask_cors import CORS

def create_app():
    """ method used to create an app instance """

    app = Flask(__name__)

    # Need to add CORS so that we can do API calls in Part 4
    CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

    # Register the namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(protected_ns, path='/api/v1/protected')

    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a strong and unique key in production
    jwt = JWTManager(app)

    return app

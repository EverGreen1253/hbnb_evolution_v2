from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns

app = Flask(__name__)
api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

# Register the namespaces
api.add_namespace(users_ns, path='/api/v1/users')
api.add_namespace(amenities_ns, path='/api/v1/amenities')

if __name__ == '__main__':
    app.run(debug=True)
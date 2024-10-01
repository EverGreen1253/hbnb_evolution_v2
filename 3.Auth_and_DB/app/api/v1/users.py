from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from app.services.facade import HBnBFacade
from app.services import facade

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

# facade = HBnBFacade()

@api.route('/')
class UserList(Resource):
    @api.expect(user_model)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Setter validation failure')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self):
        # Create the user
        # curl -X POST "http://127.0.0.1:5000/api/v1/users/" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{ "first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "password": "cowabunga", "is_admin": true}'

        # We have a chicken and egg problem here. If the claims verification is active
        # creating a new user would need you to submit a JWT. BUT! To get a JWT first,
        # you'll need to be able to login an existing user. And then you'd need to create
        # a user first. See the problem?!?!?

        """Register a new user"""
        claims = get_jwt()
        if not claims.get('is_admin', True):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload

        # Simulate email uniqueness check (to be replaced by real validation with persistence)
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        # Validate input data (first_name, last_name, email, password)
        if not all([user_data.get('first_name'), user_data.get('last_name'), user_data.get('email'), user_data.get('password')]):
            return {'error': 'Invalid input data'}, 400

        # the try catch is here in case setter validation fails
        new_user = None
        try:
            new_user = facade.create_user(user_data)
        except ValueError as error:
            return { 'error': "Setter validation failure: {}".format(error) }, 400

        return {'id': str(new_user.id), 'message': 'User created successfully'}, 201

    @api.response(200, 'Users list successfully retrieved')
    def get(self):
        # curl -X GET http://localhost:5000/api/v1/users/

        """ Get list of all users """
        all_users = facade.get_all_users()
        output = []
        for user in all_users:
            # print(user)
            output.append({
                'id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            })

        return output, 200

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        # curl -X GET http://localhost:5000/api/v1/users/<user_id>

        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return {'id': str(user.id), 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}, 200

    @api.expect(user_model)
    @api.response(200, 'User details updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Setter validation failure')
    @api.response(400, 'You cannot modify email or password.')
    @api.response(403, 'Admin privileges required')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    @jwt_required()
    def put(self, user_id):
        # curl -X PUT "http://127.0.0.1:5000/api/v1/users/<user_id>" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{ "first_name": "Reed", "last_name": "Richards" }'

        """ Update user specified by id """
        user_data = api.payload

        is_admin_user = False
        claims = get_jwt()
        if claims.get('is_admin', True):
            is_admin_user = True

        # user may only be updating one or two items and not everything
        wanted_keys_list = []
        if 'first_name' in user_data:
            wanted_keys_list.append('first_name')
        if 'last_name' in user_data:
            wanted_keys_list.append('last_name')

        if not is_admin_user:
            # don't allow changes to email or password if not Admin
            if 'email' in user_data or 'password' in user_data:
                return { 'error': "You cannot modify email or password." }, 400

            current_user = get_jwt_identity()
            if user_id != current_user['id']:
                return { 'error': "Unauthorized action" }, 403
        else:
            # users are able to update their own details (first_name, last_name)
            # but cannot change their email or password
            if 'email' in user_data:
                # make sure the email isn't already taken!
                existing_user = facade.get_user_by_email(user_data['email'])
                if existing_user:
                    return {'error': 'Email already registered'}, 400

                wanted_keys_list.append('email')
            if 'password' in user_data:
                wanted_keys_list.append('password')

        # NOTE: If the user_data contains any extra attributes aside from what is assembled
        # within wanted_keys_list, the if-else check below will throw an error.

        # Ensure that user_data contains only what we want (e.g. first_name, last_name)
        # https://stackoverflow.com/questions/10995172/check-if-list-of-keys-exist-in-dictionary
        if len(user_data) != len(wanted_keys_list) or not all(key in wanted_keys_list for key in user_data):
            return {'error': 'Invalid input data - required attributes missing'}, 400

        # Check that user exists first before updating them
        user = facade.get_user(user_id)
        if user:
            try:
                facade.update_user(user_id, user_data)
            except ValueError as error:
                return { 'error': "Setter validation failure: {}".format(error) }, 400

            return {'message': 'User updated successfully'}, 200

        return {'error': 'User not found'}, 404


# Example endpoint to show how to use relationships
# I'm calling it UserRelations because I can't think of a better name
@api.route('/<user_id>/places/')
class UserRelations(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place owner data not found')
    def get(self, user_id):
        # Log in as Admin
        # curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" -H "Content-Type: application/json" -d '{ "email": "admin@hbnb.io", "password": "admin1234" }'

        # Create a property
        # curl -X POST "http://127.0.0.1:5000/api/v1/places/" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{"title": "Cozy Apartment","description": "A nice place to stay","price": 100.0,"latitude": 37.7749,"longitude": -122.4194}'

        # Call the endpoint to see how the model relation extracts the Places data through the User model
        # curl -X GET http://localhost:5000/api/v1/users/<user_id>/places/

        """Get user's owned properties details by user ID"""
        all_places = facade.get_user_places(user_id)
        if not all_places:
            return {'error': 'The specified User does not own any Places'}, 404

        output = []
        for place in all_places:
            output.append({
                'id': str(place.id),
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude,
            })

        return output, 200

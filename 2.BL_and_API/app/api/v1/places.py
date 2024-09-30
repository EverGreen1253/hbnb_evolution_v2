from flask_restx import Namespace, Resource, fields
# from app.services.facade import HBnBFacade
from app.services import facade

api = Namespace('places', description='Place operations')

# Define the models for related entities
amenity_model = api.model('Amenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('User', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Adding the review model
review_model = api.model('Review', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

# facade = HBnBFacade()

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Setter validation failure')
    def post(self):
        # Need to add at least one user first so that we have someone in the system as an owner

        # curl -X POST "http://127.0.0.1:5000/api/v1/users/" -H "Content-Type: application/json" -d '{"first_name": "John","last_name": "Doe","email": "john.doe@example.com"}'

        # curl -X POST "http://127.0.0.1:5000/api/v1/places/" -H "Content-Type: application/json" -d '{"title": "Cozy Apartment","description": "A nice place to stay","price": 100.0,"latitude": 37.7749,"longitude": -122.4194,"owner_id": ""}'

        """Register a new place"""
        places_data = api.payload
        wanted_keys_list = ['title', 'description', 'price', 'latitude', 'longitude', 'owner_id']

        # Check whether the keys are present
        if not all(name in wanted_keys_list for name in places_data):
            return { 'error': "Invalid input data" }, 400

        # check that user exists
        user = facade.get_user(str(places_data.get('owner_id')))
        if not user:
            return { 'error': "Invalid input data - user does not exist" }, 400

        # the try catch is here in case setter validation fails
        new_place = None
        try:
            # NOTE: We're storing a user object in the owner slot and getting rid of owner_id
            places_data['owner'] = user
            del places_data['owner_id']

            new_place = facade.create_place(places_data)
        except ValueError as error:
            return { 'error': "Setter validation failure: {}".format(error) }, 400

        output = {
            'id': str(new_place.id),
            "title": new_place.title,
            "description": new_place.description,
            "price": new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            "owner_id": new_place.owner.id
        }
        return output, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        all_places = facade.get_all_places()
        output = []

        for place in all_places:
            output.append({
                'id': str(place.id),
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude,
            })

        return output, 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    @api.response(404, 'Place owner not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        owner = place.owner
        if not owner:
            return {'error': 'Place owner not found'}, 404

        amenities_list = []
        for amenity in place.amenities:
            amenities_list.append({
                'id': str(amenity.id),
                'name': amenity.name
            })

        output = {
            'id': str(place.id),
            'title': place.title,
            'description': place.description,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': str(owner.id),
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'email': owner.email
            },
            'amenities': amenities_list
        }

        return output, 200

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Setter validation failure')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        # curl -X PUT "http://127.0.0.1:5000/api/v1/places/<place_id>" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{"title": "Not So Cozy Apartment","description": "A terrible place to stay","price": 999.99}'

        """Update a place's information"""
        place_data = api.payload
        wanted_keys_list = ['title', 'description', 'price']

        if len(place_data) != len(wanted_keys_list) or not all(key in wanted_keys_list for key in place_data):
            return {'error': 'Invalid input data - required attributes missing'}, 400

        # Check that place exists first before updating them
        place = facade.get_place(place_id)
        if place:
            try:
                facade.update_place(place_id, place_data)
            except ValueError as error:
                return { 'error': "Setter validation failure: {}".format(error) }, 400

            return {'message': 'Place updated successfully'}, 200

        return {'error': 'Place not found'}, 404

from flask_restx import Namespace, Resource, fields
# from app.services.facade import HBnBFacade
from app import facade

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

# Define the place model for input validation and documentation
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities')
})

# facade = HBnBFacade()

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        # Need to add at least one user first so that we have someone in the system as an owner

        # curl -X POST "http://127.0.0.1:5000/api/v1/users/" -H "Content-Type: application/json" -d '{
        #   "first_name": "John",
        #   "last_name": "Doe",
        #   "email": "john.doe@example.com"
        # }'

        # curl -X POST "http://127.0.0.1:5000/api/v1/places/" -H "Content-Type: application/json" -d '{
        # "title": "Cozy Apartment",
        # "description": "A nice place to stay",
        # "price": 100.0,
        # "latitude": 37.7749,
        # "longitude": -122.4194,
        # "owner_id": ""
        # }'

        """Register a new place"""
        places_data = api.payload
        wanted_keys_list = ['title', 'description', 'price', 'latitude', 'longitude', 'owner_id']

        # Check whether the keys are present for price, latitude, longitude
        if not all(name in wanted_keys_list for name in places_data):
            return { 'error': "Invalid input data" }, 400

        # the try catch is here in case setter validation fails
        new_place = None
        try:
            new_place = facade.create_place(places_data)
        except ValueError as error:
            return { 'error': "Setter validation failure: {}".format(error) }, 400

        return {'id': str(new_place.id), 'message': 'Place created successfully'}, 201

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

        # This is going to be so cursed. If only there were a way to grab
        # all the data without multiple function calls...

        owner = facade.get_user(place.owner_id)
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
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information"""
        # Placeholder for the logic to update a place by ID
        pass
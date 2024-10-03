from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from app.services.facade import HBnBFacade
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

# facade = HBnBFacade()

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Amenity already exists')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Setter validation failure')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self):
        # Create the amenity
        # curl -X POST "http://127.0.0.1:5000/api/v1/amenities/" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{ "name": "Wi-Fi"}'

        """Register a new amenity"""
        claims = get_jwt()
        if not claims.get('is_admin', True):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload

        # Check if already exists
        existing_amenity = facade.get_amenity_by_name(amenity_data['name'])
        if existing_amenity:
            return {'error': 'Amenity already exists'}, 400

        # Make sure we passed in exactly what is needed
        wanted_keys_list = ['name']
        if len(amenity_data) != len(wanted_keys_list) or not all(key in wanted_keys_list for key in amenity_data):
            return {'error': 'Invalid input data'}, 400

        # the try catch is here in case setter validation fails
        new_amenity = None
        try:
            new_amenity = facade.create_amenity(amenity_data)
        except ValueError as error:
            return { 'error': "Setter validation failure: {}".format(error) }, 400

        return {'id': str(new_amenity.id), 'message': 'Amenity created successfully'}, 201

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""
        all_amenities = facade.get_all_amenities()
        output = []

        for amenity in all_amenities:
            output.append({
                'id': str(amenity.id),
                'name': amenity.name
            })

        return output, 200

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 400

        output = {
            'id': str(amenity.id),
            'name': amenity.name
        }

        return output, 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Setter validation failure')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update an amenity's information"""
        claims = get_jwt()
        if not claims.get('is_admin', True):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload
        wanted_keys_list = ['name']

        # Ensure that amenity_data contains only what we want (e.g. name)
        if len(amenity_data) != len(wanted_keys_list) or not all(key in wanted_keys_list for key in amenity_data):
            return {'error': 'Invalid input data - required attributes missing'}, 400

        # Check that user exists first before updating them
        amenity = facade.get_amenity(amenity_id)
        if amenity:
            try:
                facade.update_amenity(amenity_id, amenity_data)
            except ValueError as error:
                return { 'error': "Setter validation failure: {}".format(error) }, 400

            return {'message': 'Amenity updated successfully'}, 200

        return {'error': 'Amenity not found'}, 404

# Example endpoints to show how to use relationships
@api.route('/<amenity_id>/<relation>/')
class AmenityRelations(Resource):
    @api.response(404, 'Unable to retrieve Places using this Amenity')
    def get(self, amenity_id, relation):
        """
        Only one endpoint for now, to get the places using the specified amenity
        """

        output = []

        # === PLACES ===
        # curl -X GET http://localhost:5000/api/v1/amenities/<amenity_id>/places/

        if relation == "places":
            all_places = facade.get_places_with_specific_amenity(amenity_id)
            if not all_places:
                return {'error': 'Unable to retrieve Places using this Amenity'}, 404

            for place in all_places:
                output.append({
                    'id': str(place.id),
                    'title': place.title,
                    'latitude': place.latitude,
                    'longitude': place.longitude,
                })

        return output, 200

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):

        # Create the user
        # curl -X POST "http://127.0.0.1:5000/api/v1/users/" -H "Content-Type: application/json" -d '{ "first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "password": "cowabunga"}'

        # Log the user in
        # curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" -H "Content-Type: application/json" -d '{ "email": "john.doe@example.com", "password": "cowabunga" }'

        # Curl command to create a new place (needs JWT of logged-in owner)
        # curl -X POST "http://127.0.0.1:5000/api/v1/places/" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{"title": "Cozy Apartment","description": "A nice place to stay","price": 100.0,"latitude": 37.7749,"longitude": -122.4194}'

        """Register a new place"""
        places_data = api.payload
        current_user = get_jwt_identity()

        # adding owner_id back in so that places_data still plays nice with the old code
        places_data['owner_id'] = current_user['id']

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
            # We don't need this for DB storage...
            # NOTE: We're storing a user object in the owner slot and getting rid of owner_id
            # places_data['owner'] = user
            # del places_data['owner_id']

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
            "owner_id": new_place.owner_id
        }
        return output, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        all_places = facade.get_all_places()
        output = []

        for place in all_places:
            # For Part 4: What if we want to include the amenities of each place in the output?
            amenities_list = []
            all_amenities = facade.get_place_amenities(place.id)
            for amenity in all_amenities:
                amenities_list.append(amenity.name)

            output.append({
                'id': str(place.id),
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude,

                # For Part 4: additional data needed for Place listing Card
                'description': place.description,
                'price': place.price,
                'amenities': amenities_list
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
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @jwt_required()
    def put(self, place_id):
        # curl -X PUT "http://127.0.0.1:5000/api/v1/places/<place_id>" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{"title": "Not So Cozy Apartment","description": "A terrible place to stay","price": 999.99}'

        """Update a place's information"""
        claims = get_jwt()
        current_user = get_jwt_identity()

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if not claims.get('is_admin', True) and place.owner_id != current_user['id']:
            return {'error': 'Unauthorized action'}, 403

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

# Example endpoints to show how to use relationships
@api.route('/<place_id>/<relation>/')
class PlaceRelations(Resource):
    @api.response(404, 'Unable to retrieve Amenities linked to this property')
    @api.response(404, 'Unable to retrieve Reviews written about this place')
    @api.response(404, 'Unable to retrieve Owner details for this property')
    def get(self, place_id, relation):
        """
        Depending on the term used in <relation>, we either retrieve 
        the owner User of the Place, or the Reviews for it
        """

        output = []

        # === AMENITIES ===
        if relation == "amenities":
            # Manually add the place_id-to-amenity_id records in the DB. This is the fastest way to do it.

            # Get the list of amenities that can be found in this place
            # curl -X GET http://localhost:5000/api/v1/places/<place_id>/amenities/
            all_amenities = facade.get_place_amenities(place_id)
            if not all_amenities:
                return {'error': 'Unable to retrieve Amenities linked to this property'}, 404

            for amenity in all_amenities:
                output.append({
                    'id': str(amenity.id),
                    'name': amenity.name
                })

        # === REVIEWS ===
        if relation == "reviews":
            # Get the list of reviews written about this place
            # curl -X GET http://localhost:5000/api/v1/places/<place_id>/reviews/

            all_reviews = facade.get_place_reviews(place_id)
            if not all_reviews:
                return {'error': 'Unable to retrieve Reviews written about this place'}, 404

            for review in all_reviews:
                output.append({
                    'id': str(review.id),
                    'text': review.text,
                    'rating': review.rating
                })

        # === OWNER ===
        if relation == "owner":
            # Get the details of the owner of this place
            # curl -X GET http://localhost:5000/api/v1/places/<place_id>/owner/

            owner = facade.get_place_owner(place_id)
            if not owner:
                return {'error': 'Unable to retrieve Owner details for this property'}, 404

            output = {
                'id': str(owner.id),
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'email': owner.email
            }

        return output, 200


# The endpoint below is used only for Part 4
@api.route('/search')
class PlaceSearch(Resource):
    @api.response(200, 'Search completed')
    @api.response(400, 'Invalid input data')
    def post(self):
        # Query the database based on the data passed in
        # curl -X POST "http://127.0.0.1:5000/api/v1/places/search" -H "Content-Type: application/json" -d '{ "name": "cozy", "price": "250", "amenities": ["wi-fi", "toilet"]}'

        # --- IMPORTS ---
        from sqlalchemy import text
        from app.persistence import db_session

        search_data = api.payload
        # print(search_data)

        name = search_data['name'].strip()
        price = int(search_data['price'])
        amenities = search_data['amenities']

        # --- Example query ---
        # SELECT * FROM (
        #     SELECT p.*, GROUP_CONCAT(a.name) AS amenities, GROUP_CONCAT(b.name) AS selected_amenities
        #     FROM places p
        #     LEFT JOIN place_amenity pa ON p.id = pa.place_id
        #     LEFT JOIN amenities a ON pa.amenity_id  = a.id
        #     LEFT JOIN (
        #         SELECT * FROM amenities
        #         WHERE amenities.name IN ('wi-fi', 'toilet')
        #     ) b ON pa.amenity_id  = b.id
        #     GROUP BY p.id
        # ) as x
        # WHERE (title LIKE "%cozy%" OR description LIKE "%cozy%") AND (price >= 250)

        where_clause = ""
        and_clause = ""
        name_conditions = ""
        price_conditions = ""
        amenities_condition = ""
        amenities_and_clause = ""
        amenities_present_condition = ""

        if len(name) > 0:
            # add WHERE clause
            if where_clause == "":
                where_clause = "WHERE "
            name_conditions = "(title LIKE \"%" + name + "%\" OR description LIKE \"%" + name + "%\")"

        if price > 0:
            # add WHERE clause or AND clause
            if where_clause == "":
                where_clause = "WHERE "
            else:
                and_clause = "AND "
            price_conditions = "(price >= " + str(price) + ")"

        if len(amenities) > 0:
            # Assemble the comma-separated list
            # 1. wrap each item in the list with inverted commas
            amenities_list = []
            for a in amenities:
                amenities_list.append("'" + a + "'")

            # 2. then turn it into a comma separated string
            amenities_comma_list = ",".join(amenities_list)
            amenities_condition = "WHERE amenities.name IN (" + amenities_comma_list + ")"

            # 3. add a final clause in the WHERE
            if where_clause == "":
                where_clause = "WHERE "
            else:
                amenities_and_clause = "AND "
            amenities_present_condition = "(selected_amenities != '')"

        conditions = where_clause + name_conditions + and_clause + price_conditions + amenities_and_clause + amenities_present_condition

        query = "SELECT * FROM ( \
            SELECT p.*, GROUP_CONCAT(a.name) AS amenities, GROUP_CONCAT(b.name) AS selected_amenities \
            FROM places p \
            LEFT JOIN place_amenity pa ON p.id = pa.place_id \
            LEFT JOIN amenities a ON pa.amenity_id  = a.id \
            LEFT JOIN ( \
                SELECT * FROM amenities \
                " + amenities_condition + " \
            ) b ON pa.amenity_id  = b.id \
            GROUP BY p.id \
        ) as x " + conditions

        # print(query)

        output = []
        sql = text(query)
        result = db_session.execute(sql)

        # print(result)

        for row in result:
            amenities_array = []
            if row.amenities:
                amenities_array = row.amenities.split(",")

            output.append({
                "place_id": row.id,
                "title": row.title,
                "description": row.description,
                "price": row.price,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "owner_id": row.owner_id,
                "amenities": amenities_array
            })

        return output, 200

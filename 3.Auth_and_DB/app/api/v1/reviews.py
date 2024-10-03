from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from app.services.facade import HBnBFacade
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# facade = HBnBFacade()

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'You cannot review your own place.')
    @api.response(400, 'You have already reviewed this place.')
    @jwt_required()
    def post(self):
        # curl -X POST "http://127.0.0.1:5000/api/v1/reviews/" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{ "text": "Very dirty", "rating": 1, "place_id": "<place_id_goes_here>" }'

        """Register a new review"""
        current_user = get_jwt_identity()
        review_data = api.payload
        review_data['user_id'] = current_user['id']

        wanted_keys_list = ['text', 'rating', 'user_id', 'place_id']

        # check that required attributes are present
        if not all(name in wanted_keys_list for name in review_data):
            return { 'error': "Invalid input data - required attributes missing" }, 400

        # check that place exists
        place = facade.get_place(str(review_data.get('place_id')))
        if not place:
            return { 'error': "Invalid input data - place does not exist" }, 400
        if place.owner_id == current_user['id']:
            return {'error': 'You cannot review your own place.'}, 400

        # check that this particular logged-in user hasn't already reviewed it before
        # I have the worst possible way to do it, but it will work:
        # Get ALL reviews, then search through them for user_id and place_id combo
        all_reviews = facade.get_all_reviews()
        for review in all_reviews:
            if review.user_id == current_user['id'] and review.place_id == review_data['place_id']:
                return { 'error': "You have already reviewed this place." }, 400

        # finally, create the review
        new_review = None
        try:
            new_review = facade.create_review(review_data)
        except ValueError as error:
            return { 'error': "Setter validation failure: {}".format(error) }, 400

        return {'id': str(new_review.id), 'message': 'Review created successfully'}, 201

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        all_reviews = facade.get_all_reviews()
        output = []

        for review in all_reviews:
            output.append({
                'id': str(review.id),
                'text': review.text,
                'rating': review.rating
            })

        return output, 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        output = {
            'id': str(review.id),
            'text': review.text,
            'rating': review.rating,
            'user_id': review.user_id,
            'place_id': review.place_id,
        }

        return output, 200

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, review_id):
        # curl -X PUT "http://127.0.0.1:5000/api/v1/reviews/<review_id>" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>" -d '{ "text": "So lovely!", "rating": 5 }'

        """Update a review's information"""
        claims = get_jwt()
        current_user = get_jwt_identity()

        # Check that review exists first before updating them
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not claims.get('is_admin', True) and review.user_id != current_user['id']:
            return { 'error': "Unauthorized action" }, 403

        review_data = api.payload
        wanted_keys_list = ['text', 'rating']

        # check that required attributes are present
        if not all(name in wanted_keys_list for name in review_data):
            return { 'error': "Invalid input data - required attributes missing" }, 400

        try:
            facade.update_review(review_id, review_data)
        except ValueError as error:
            return { 'error': "Setter validation failure: {}".format(error) }, 400

        return {'message': 'Review updated successfully'}, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        # curl -X DELETE "http://127.0.0.1:5000/api/v1/reviews/<review_id>" -H "Content-Type: application/json" -H "Authorization: Bearer <token_goes_here>"

        """Delete a review"""
        current_user = get_jwt_identity()

        # Check that review exists first
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        if review.user_id != current_user['id']:
            return { 'error': "Unauthorized action" }, 403

        try:
            facade.delete_review(review_id)
        except ValueError:
            return { 'error': "Review not found" }, 400

        return {'message': 'Review deleted successfully'}, 200

# NOTE: This endpoint can be redone using model relationships.
# It is now found in api/v1/places.py
# @api.route('/places/<place_id>/reviews')
# class PlaceReviewList(Resource):
#     @api.response(200, 'List of reviews for the place retrieved successfully')
#     @api.response(404, 'Place not found')
#     def get(self, place_id):
#         """Get all reviews for a specific place"""
#         # I'm going to do this the worst possible way:
#         # 1. grab all the reviews records (lol)
#         # 2. iterate them all through a loop while searching for the place_id
#         # 3. save the ones with the place_id in an array
#         # 4. print it out

#         all_reviews = facade.get_all_reviews()
#         output = []

#         for review in all_reviews:
#             if review.place_id == place_id:
#                 output.append({
#                     'id': str(review.id),
#                     'text': review.text,
#                     'rating': review.rating
#                 })

#         if len(output) == 0:
#             return { 'error': "Place not found" }, 400

#         return output, 200

# Example endpoints to show how to use relationships
@api.route('/<review_id>/<relation>/')
class ReviewRelations(Resource):
    @api.response(404, 'Unable to retrieve Writer details for this Review')
    @api.response(404, 'Unable to retrieve Place linked to this Review')
    def get(self, review_id, relation):
        """
        Depending on the term used in <relation>, we either retrieve 
        the writer the Review, or Place associated with it
        """

        output = []

        # === WRITER ===
        if relation == "writer":
            # Get the details of the owner of this place
            # curl -X GET http://localhost:5000/api/v1/reviews/<review_id>/writer/

            writer = facade.get_review_writer(review_id)
            if not writer:
                return {'error': 'Unable to retrieve Writer details for this Review'}, 404

            output = {
                'id': str(writer.id),
                'first_name': writer.first_name,
                'last_name': writer.last_name,
                'email': writer.email
            }

        # === PLACES ===
        if relation == "place":
            # Get the details of the owner of this place
            # curl -X GET http://localhost:5000/api/v1/reviews/<review_id>/place/

            place = facade.get_reviewed_place(review_id)
            if not place:
                return {'error': 'Unable to retrieve Place linked to this Review'}, 404

            output = {
                'id': str(place.id),
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude,
            }

        return output, 200

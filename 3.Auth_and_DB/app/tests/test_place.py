#!/usr/bin/python3
""" Unittests for HBnB Evolution v2 Part 2 """

import unittest
from models.place import Place
from models.user import User
from models.review import Review

class TestPlace(unittest.TestCase):
    """Test that the Place model works as expected
    """

    def test_create_place(self):
        """Tests creation of Place instances """
        owner = User(first_name="Alice", last_name="Smith", email="alice.smith@example.com")
        place = Place(title="Cozy Apartment", description="A nice place to stay", price=100.00, latitude=37.7749, longitude=-122.4194, owner_id=owner.id)

        # Adding a review
        review = Review(text="Great stay!", rating=5, place_id=place.id, user_id=owner.id)
        place.add_review(review)

        assert place.title == "Cozy Apartment"
        assert place.price == 100.00
        assert len(place.reviews) == 1
        assert place.reviews[0].text == "Great stay!"
        print("Place creation and relationship test passed!")

    # TODO: add more tests

if __name__ == '__main__':
    unittest.main()

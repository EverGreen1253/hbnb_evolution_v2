-- General notes --
Notice that for the models, the value assignment statements in the constructor differ from the ones in the setter.
e.g. self.description = description  VS  self._description = value

The one in the constructor is actually calling the setter, and the one in the setter is actually saving the value to the internal _description attribute. The name shown to the outside world is actually invoking the getters and setters while internally the attribute's name has an underscore prefix.


-- User model --
Pretty straight forward for most of the model. Note that a very simple regular expression is used to validate the email address.

The two static methods in the model (email_exists, user_exists) have hardcoded return values for now because at this point we haven't designed how all the User objects are going to be stored and thus have no proper way of searching through all of them to find the data we need.


-- Place model --
Similar in structure to the other models and has a LOT of attributes.

There is one static method to take note of (place_exists) and this one has a hardcoded return value too because at this point there is no proper design as to how all the Place objects are to be organised in the system.


-- Review model --
Nothing special.


-- Amenity model --
Nothing special.
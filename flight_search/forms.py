"""Flask-WTF search form. CSRF is required (D4); business rules live in validator."""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchForm(FlaskForm):
    departure_city = StringField("Departure city")
    arrival_city = StringField("Arrival city")
    travel_date = StringField("Travel date")
    passengers = StringField("Passengers")
    submit = SubmitField("Search Flights")

"""
Defines forms used by various web pages.

Each class is a form.
"""

from flask_wtf import FlaskForm
from wtforms import (DecimalField, IntegerField, SubmitField, SelectField)
from wtforms.validators import input_required, number_range


class StartRideForm(FlaskForm):
    """
    "Start ride" button.
    """
    submit = SubmitField('Start ride')


class EndRideForm(FlaskForm):
    """
    End ride form for the user to fill out.
    """
    longitude = DecimalField(label='Longitude', validators=[
        input_required(),
        number_range(min=-180, max=180,
                     message="Longitude must be between -180 and 180.")])
    latitude = DecimalField(label='Latitude', validators=[
        input_required(),
        number_range(min=-90, max=90,
                     message="Latitude must be between -90 and 90.")])
    battery = IntegerField(label='Battery (percent)', validators=[
        input_required(),
        number_range(min=0, max=100,
                     message="Battery (percent) must be between 0 and 100.")])
    submit = SubmitField('End ride')


class SeeVehicleForm(FlaskForm):
    """
    Button to see information on a single vehicle.
    """
    submit = SubmitField('See Vehicle')


class VehicleForm(FlaskForm):
    """
    Register a new vehicle.
    """
    vehicle_type = SelectField(label='Type',
                               choices=[('scooter', 'Scooter')])
    longitude = DecimalField(label='Longitude', validators=[
        input_required(),
        number_range(min=-180, max=180,
                     message="Longitude must be between -180 and 180.")])
    latitude = DecimalField(label='Latitude', validators=[
        input_required(),
        number_range(min=-90, max=90,
                     message="Latitude must be between -90 and 90.")])
    battery = IntegerField(label='Battery (percent)', validators=[
        input_required(),
        number_range(min=0, max=100,
                     message="Battery (percent) must be between 0 and 100.")])
    submit = SubmitField('Add vehicle')


class RemoveVehicleForm(FlaskForm):
    """
    Button to delete a vehicle.
    """
    submit = SubmitField('Remove vehicle')

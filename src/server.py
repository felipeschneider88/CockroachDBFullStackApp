#!/usr/bin/env python3
"""
Runs the MovR web server on your local machine.

Uses the .env file from the current directory to supplement
    environment variables while running.

Usage:
    ./server.py run [options]
    ./server.py --help

Options:
    -h --help               Show this text.
    --port <port>           Port where the server listens for requests.
                                [default: 36257]
    --url <url>             CockroachDB connection string. If none, it will use
                                the .env file or the DB_URL environment
                                variable.
    --max-records <number>  Maximum number of records to query when no filter
                                is specified [default: 20]
"""

from docopt import docopt
from flask import (Flask, flash, redirect, render_template,
                   url_for)
from flask_bootstrap import Bootstrap, WebCDN
from sqlalchemy.exc import IntegrityError, ProgrammingError

from movr.movr import MovR
from util.calculations import generate_end_ride_messages
from util.connect_with_sqlalchemy import (build_sqla_connection_string,
                                          test_connection)
from util.exception_handling import render_error_page
from web.config import Config
from web.forms import (EndRideForm, RemoveVehicleForm, SeeVehicleForm,
                       StartRideForm, VehicleForm)

# Initialize the web server app & load bootstrap
app = Flask(__name__)
Bootstrap(app)

# Parse the command line options
_opts = docopt(__doc__)
_PORT = int(_opts['--port'])
_URL = _opts['--url']
_MAX_RECORDS = _opts['--max-records']
_DEFAULT_ROUTE = 'vehicles'

# Configure the app
app.config.from_object(Config)

if _URL is None:  # No --url flag; check for environment variable DB_URI
    environment_connection_string = app.config.get('DB_URI')
    CONNECTION_STRING = build_sqla_connection_string(
        environment_connection_string)
else:  # url was passed with `--url`
    CONNECTION_STRING = build_sqla_connection_string(_URL)
# Load environment variables from .env file

# Instantiate the movr object defined in movr/movr.py
movr = MovR(CONNECTION_STRING, max_records=_MAX_RECORDS)

app.extensions['bootstrap']['cdns']['bootstrap'] = WebCDN(
    '//getbootstrap.com/docs/4.5/dist/'
)

# Verify connection to database is working.
# Suggest help if common errors are encountered.
test_connection(movr.engine)


# ROUTES
# Home page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home_page():
    """Redirects to appropriate default page."""
    return redirect(url_for(_DEFAULT_ROUTE, _external=True))


# Vehicles page
@app.route('/vehicles', methods=['GET'])
def vehicles(max_vehicles=_MAX_RECORDS):
    """
    Shows the vehicles page, listing all vehicles.
    """
    try:
        start_ride_form = StartRideForm()
        see_vehicle_form = SeeVehicleForm()
        some_vehicles = movr.get_vehicles(max_vehicles=max_vehicles)
        return render_template('vehicles.html',
                               title='Vehicles',
                               vehicles=some_vehicles,
                               start_ride_form=start_ride_form,
                               see_vehicle_form=see_vehicle_form)
    except ProgrammingError as error:
        return render_error_page(error, movr)


# Single vehicle page
@app.route('/vehicle/<vehicle_id>', methods=['GET', 'POST'])
def vehicle(vehicle_id):
    """View information for a single vehicle."""
    start_ride_form = StartRideForm()
    remove_vehicle_form = RemoveVehicleForm()
    this_vehicle, location_history = movr.get_vehicle_and_location_history(
        vehicle_id, max_locations=_MAX_RECORDS)
    if this_vehicle is None:  # not in database
        flash("Vehicle `{}` not found.".format(vehicle_id))
        return redirect(url_for('vehicles', _external=True))
    return render_template('vehicle.html',
                           title='Vehicle {}'.format(vehicle_id),
                           vehicle=this_vehicle,
                           locations=location_history,
                           start_ride_form=start_ride_form,
                           remove_vehicle_form=remove_vehicle_form)


# Remove a vehicle
@app.route('/vehicle/remove/<vehicle_id>', methods=['POST'])
def remove_vehicle(vehicle_id):
    """Delete a vehicle from the database."""
    vehicle_deleted = movr.remove_vehicle(vehicle_id)
    if vehicle_deleted:  # Vehicle looks like it was deleted
        # Verify that it was actually deleted as required by the lab.
        if movr.get_vehicle(vehicle_id) is None:  # Vehicle looks deleted
            flash("Deleted vehicle with id "
                  "`{id}` from database.".format(id=vehicle_id))
            return redirect(url_for('vehicles', _external=True))
        # else vehicle is still in the database.
        flash(("Vehicle `{}` NOT successfully deleted. Please modify "
               "remove_vehicle_txn in `movr/transactions.py` to implement "
               "the correct functionality."
               ).format(vehicle_id))
        return redirect(url_for('vehicle', vehicle_id=vehicle_id,
                                _external=True))
    elif vehicle_deleted is None:  # Vehicle in use or not in database
        flash(("Vehicle `{}` not found in database, or is currently in use. "
               "Cannot delete it.").format(vehicle_id))
        return redirect(url_for('vehicles', _external=True))

    return render_error_page(RuntimeError(
        ("Attempt to remove vehicle hit unexpected state. "
         "Please notify university@cockroachlabs.com via email of this error "
         "message. Attempted to remove vehicle `{vehicle_id}`. "
         "Current row state is `{row}`."
         ).format(vehicle_id=vehicle_id,
                  row=movr.get_vehicle(vehicle_id))),
                             movr)


# Start ride route
@app.route('/ride/start/<vehicle_id>', methods=['POST'])
def start_ride(vehicle_id):
    """
    When the user clicks "start ride," perform DB op & redirect to ride page.
    """
    if movr.start_ride(vehicle_id):
        flash('Ride started with vehicle {}.'.format(vehicle_id))
        return redirect(url_for('ride', vehicle_id=vehicle_id, _external=True))

    flash('Could not start ride on vehicle {}.'.format(vehicle_id))
    flash('Either the vehicle is actively being ridden, or it has been '
          'deleted from the database.')
    return redirect(url_for('vehicles', _external=True))


# Ride page
@app.route('/ride/<vehicle_id>', methods=['GET', 'POST'])
def ride(vehicle_id):
    """
    Show the user the form to end a ride.
    """
    form = EndRideForm()
    vehicle_at_start = movr.get_vehicle(vehicle_id)
    if vehicle_at_start is None:  # Vehicle not found in database
        flash("Vehicle `{}` not found.".format(vehicle_id))
        return redirect(url_for('vehicles', _external=True))
    elif not vehicle_at_start['in_use']:  # Ride hasn't started.
        flash("Cannot view the ride for this vehicle. It is not currently in "
              "use.")
        return redirect(url_for('vehicle', vehicle_id=vehicle_id,
                                _external=True))

    if form.validate_on_submit():
        try:
            if movr.end_ride(vehicle_id, form.longitude.data, form.latitude.data,
                             form.battery.data):
                vehicle_at_end = movr.get_vehicle(vehicle_id)
                for message in generate_end_ride_messages(vehicle_at_start,
                                                          vehicle_at_end):
                    flash(message)
                return redirect(url_for('vehicle', vehicle_id=vehicle_id,
                                        _external=True))
            # else: end_ride didn't work
            flash("Unable to end ride for vehicle `{id}`.".format(id=vehicle_id))
            return redirect(url_for('ride', vehicle_id=vehicle_id, _external=True))
        except ValueError as e:
            return render_error_page(e, movr)
    return render_template('ride.html',
                           title=('Riding a {}'
                                  ).format(vehicle_at_start["vehicle_type"]),
                           form=form, vehicle=vehicle_at_start, _external=True)


# Add vehicles route
@app.route('/vehicles/add', methods=['GET', 'POST'])
def add_vehicle():
    """Add a new vehicle to the fleet."""
    form = VehicleForm()
    if form.validate_on_submit():
        try:
            new_info = movr.add_vehicle(vehicle_type=form.vehicle_type.data,
                                        longitude=form.longitude.data,
                                        latitude=form.latitude.data,
                                        battery=form.battery.data)
        except IntegrityError as e:
            return render_error_page(e, movr)
        vehicle_id = new_info['vehicle_id']

        # check to verify that vehicle was added
        new_vehicle = movr.get_vehicle(vehicle_id)
        if new_vehicle is None:  # Insert didn't work
            flash(("Vehicle with id `{}` "
                   "NOT successfully added. Edit add_vehicle_txn in "
                   "movr/transactions.py to add the vehicle to the database."
                   ).format(vehicle_id))
            redirect(url_for('add_vehicle', _external=True))
        else:  # Inserted vehicle was found
            flash('Vehicle added! \nid: {}'.format(vehicle_id))
            return redirect(
                url_for('vehicle', vehicle_id=vehicle_id, _external=True))

    # form not properly filled out yet
    return render_template('add_vehicle.html',
                           title='Add a vehicle',
                           form=form)


if __name__ == '__main__':
    app.run(use_reloader=False, port=_PORT)

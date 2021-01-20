"""
Defines the transactions that are performed by movr.

This is where the python code meets the database.
"""

from uuid import uuid4

from sqlalchemy.sql.expression import func

from movr.models import Vehicle


def start_ride_txn(session, vehicle_id):
    """
    Start a vehicle ride (or continue if the vehicle is already in use).

    Arguments:
        session {.Session} -- The active session for the database connection.
        vehicle_id {String} -- The vehicle's `id` column.
    """
    # find the row where we want to start the ride.
    # SELECT * FROM vehicles WHERE id = <vehicle_id> AND in_use = false
    #         LIMIT 1;
    vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id). \
                                     filter(Vehicle.in_use == False).first()

    if vehicle is None:
        return None

    # perform the update
    # UPDATE vehicles SET in_use = true, last_checkin = now()
    #               WHERE id = <vehicle_id> AND in_use = false
    #               LIMIT 1;
    vehicle.in_use = True
    vehicle.last_checkin = func.now()

    return True  # Just making it explicit that this worked.


def end_ride_txn(session, vehicle_id, new_longitude, new_latitude,
                 new_battery):
    """
    Update a row of the rides table, and update a row of the vehicles table.

    Arguments:
        session {.Session} -- The active session for the database connection.
        vehicle_id {String} -- The vehicle's `id` column
        new_longitude {Float} -- The longitude where the ride ended
        new_latitude {Float} -- The latitude where the ride ended
        new_battery {Integer} -- The vehicle's battery % when the ride ended

    Returns:
        {Boolean} -- True if the ride ended.
    """
    # find the row
    # SELECT * FROM vehicles WHERE id = <vehicle_id> AND in_use = true;
    vehicle = session.query(Vehicle). \
                      filter(Vehicle.id == vehicle_id). \
                      filter(Vehicle.in_use == True).first()

    if vehicle is None:
        return False

    # perform the update on the row that matches the query above.
    # UPDATE vehicles SET last_longitude = <new_longitude>,
    #                     last_latitude = <new_latitude>,
    #                     battery = <new_battery>,
    #                     in_use = false,
    #                     last_checkin = now()
    #               WHERE vehicle_id = <vehicle_id>
    #                 AND in_use = true;
    vehicle.last_longitude = new_longitude
    vehicle.last_latitude = new_latitude
    vehicle.battery = new_battery
    vehicle.in_use = False
    vehicle.last_checkin = func.now()

    return True  # Just making it explicit that this worked.


def add_vehicle_txn(session, vehicle_type, longitude, latitude, battery):
    """
    Insert a row into the vehicles table.

    Arguments:
        session {.Session} -- The active session for the database connection.
        vehicle_type {String} -- The vehicle's type.

    Returns:
        vehicle_id {UUID} -- The vehicle's new UUID
    """
    vehicle_id = uuid4()  # Generate new uuid
    current_time = func.now()  # Current time on database
    new_row = Vehicle(id=str(vehicle_id),
                      last_longitude=longitude,
                      last_latitude=latitude,
                      last_checkin=current_time,
                      in_use=False,
                      vehicle_type=vehicle_type,
                      battery=battery)

    # TO COMPLETE THE "ADD VEHICLES" LAB, WRITE THE COMMAND TO INSERT THE NEW
    # ROW HERE.
    # YOU WILL NEED TO USE THE `session` OBJECT.
    # YOU MAY FIND THIS LINK IN THE SQLALCHEMY DOCS USEFUL:
    # https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session.add

    return str(vehicle_id)  # Return the new id.


def remove_vehicle_txn(session, vehicle_id):
    """
    Deletes a vehicle row from the vehicles table.

    Arguments:
        session {.Session} -- The active session for the database connection.
        vehicle_id {UUID} -- The vehicle's unique ID.

    Returns:
        {None} -- vehicle isn't found
        True {Boolean} -- vehicle is deleted
    """
    # find the row.
    # SELECT * FROM vehicles WHERE id = <vehicle_id> AND in_use = false;
    vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id). \
                                     filter(Vehicle.in_use == False).first()

    if vehicle is None:  # Either vehicle is in use or it's been deleted
        return None

    # Vehicle has been found. Delete it.

    # TO COMPLETE THE "REMOVE VEHICLES" LAB, WRITE THE COMMAND 
    # TO DELETE THE CORRECT VEHICLE HERE.
    # YOU WILL NEED TO USE THE 'session' OBJECT.
    # YOU MAY FIND THIS LINK IN THE SQLALCHEMY DOCS USEFUL:
    # https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session.delete

    return True  # Should return True when vehicle is deleted.


def get_vehicles_txn(session, max_records):
    """
    Select all rows of the vehicles table.

    Arguments:
        session {.Session} -- The active session for the database connection.
        max_records {Integer} -- Limits the number of records returned.

    Returns:
        {list} -- A list of dictionaries containing vehicle information.
    """
    # SELECT * FROM vehicles LIMIT max_records;
    vehicles = session.query(Vehicle).limit(max_records).all()

    # Return the results in a form that will persist.
    return list(map(lambda vehicle: {'id': vehicle.id,
                                     'last_longitude': vehicle.last_longitude,
                                     'last_latitude': vehicle.last_latitude,
                                     'last_checkin': vehicle.last_checkin,
                                     'in_use': vehicle.in_use,
                                     'battery': vehicle.battery,
                                     'vehicle_type': vehicle.vehicle_type},
                    vehicles))


def get_vehicle_txn(session, vehicle_id):
    """
    For when you just want a single vehicle.

    Arguments:
        session {.Session} -- The active session for the database connection.
        vehicle_id {String} -- The vehicle's `id` column.

    Returns:
        {dict} or {None} -- Contains vehicle information for the vehicle
                                queried, or None of no vehicle found.
    """
    # Find the row
    # SELECT * FROM vehicles WHERE id = <vehicle_id>;
    vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    # Return the row as a dictionary for flask to populate a page.
    if vehicle is None:
        return None

    return {'id': str(vehicle.id),
            'last_longitude': vehicle.last_longitude,
            'last_latitude': vehicle.last_latitude,
            'last_checkin': vehicle.last_checkin, 'in_use': vehicle.in_use,
            'battery': vehicle.battery,
            'vehicle_type': vehicle.vehicle_type}

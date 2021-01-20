from geopy.distance import distance


def calculate_distance(longitude_1, latitude_1, longitude_2, latitude_2):
    """
    Finds the distance, in km, btween two points on the globe.

    Inputs
    ------

    longitude_1 (float): Longitude coordinate of point 1.

    latitude_1 (float): Latitude coordinate of point 1.

    longitude_2 (float): Longitude coordinate of point 2.

    latitude_2 (float): Latitude coordinate of point 2.

    Returns
    -------

    Distance in kilometers, at a precision of 10 meters.
    """
    return round(distance((latitude_1, longitude_1),
                          (latitude_2, longitude_2)).km, 2)


def calculate_duration_minutes(start_time, end_time):
    """
    Calculates how many minutes something took.
    """
    return (end_time - start_time).total_seconds() / 60


def calculate_duration_hours(start_time, end_time):
    """
    Calculates how many hours something took.
    """
    return (end_time - start_time).total_seconds() / 3600


def calculate_velocity(start_longitude, start_latitude, start_time,
                       end_longitude, end_latitude, end_time):
    """
    Finds the magnitude of the velicty, in kilometers per hour.
    """
    distance_traveled = calculate_distance(start_longitude, start_latitude,
                                           end_longitude, end_latitude)
    duration = calculate_duration_hours(start_time, end_time)
    if duration == 0:
        raise ValueError("Cannot calculate an average velocity when the time"
                         "interval is 0.")
    return distance_traveled / duration


def generate_end_ride_messages(vehicle_at_start, vehicle_at_end):
    """
    End this ride.

    Inputs
    ------

    vehicle_at_start (dict): row information for the vehicle, contained as a
        dicttionary.

    vehicle_at_end (dict): Same format as vehicle_at_start, but after the row
        has been updated for the ride.
    """
    # Capture the state of the start of the ride
    vehicle_id = vehicle_at_start['id']
    start_longitude = vehicle_at_start['last_longitude']
    start_latitude = vehicle_at_start['last_latitude']
    start_time = vehicle_at_start['last_checkin']

    # End the ride in the database & capture that data
    end_longitude = vehicle_at_end['last_longitude']
    end_latitude = vehicle_at_end['last_latitude']
    end_time = vehicle_at_end['last_checkin']

    # Calculate distance traveled.
    distance_traveled = calculate_distance(start_longitude, start_latitude,
                                           end_longitude, end_latitude)

    # Calculate change of time & average speed
    ride_minutes = round(calculate_duration_minutes(start_time, end_time), 2)
    average_velocity = round(calculate_velocity(start_longitude, start_latitude,
                                                start_time, end_longitude,
                                                end_latitude, end_time), 2)

    # Redirect to vehicles & notify user of ride summary.
    messages = [("You have completed your ride on vehicle {id}."
                 ).format(id=vehicle_id)]
    messages.append(("You traveled {distance} km in {duration} minutes, "
                     "for an average velocity of {speed} km/h."
                     ).format(distance=distance_traveled,
                              duration=ride_minutes, speed=average_velocity))
    return messages

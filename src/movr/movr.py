"""
Defines the connection to the database for the MovR app.
"""
from cockroachdb.sqlalchemy import run_transaction
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry
from sqlalchemy.orm import sessionmaker

from movr.transactions import (add_vehicle_txn, end_ride_txn, get_vehicle_txn,
                               get_vehicles_txn, remove_vehicle_txn,
                               start_ride_txn,
                               get_vehicle_and_location_history_txn)

registry.register("cockroachdb", "cockroachdb.sqlalchemy.dialect",
                  "CockroachDBDialect")


class MovR:
    """
    Wraps the database connection. The class methods wrap transactions.
    """
    def __init__(self, conn_string, max_records=20):
        """
        Establish a connection to the database, creating an Engine instance.

        Arguments:
            conn_string {String} -- CockroachDB connection string.
        """
        self.engine = create_engine(conn_string, convert_unicode=True)
        self.connection_string = conn_string
        self.max_records = max_records

    def start_ride(self, vehicle_id):
        """
        Wraps a `run_transaction` call that starts a ride.

        Arguments:
            vehicle_id {UUID} -- The vehicle's unique ID.
        """
        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: start_ride_txn(session, vehicle_id))

    def end_ride(self, vehicle_id, new_longitude, new_latitude, new_battery):
        """
        Wraps a `run_transaction` call that ends a ride.

        Updates position (lat & long), battery & timestamp.

        Arguments:
            vehicle_id {UUID} -- The vehicle's unique ID.
            new_longitude {float} -- Vehicle's new longitude coordinate
            new_latitude {float} -- Vehicle's new latitude coordinate
            new_battery {int} -- Vehicle's new battery reading

        Returns:
            {datetime} -- Timestamp of the end of the ride from the server.
        """
        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: end_ride_txn(session, vehicle_id, new_longitude,
                                         new_latitude, new_battery))

    def remove_vehicle(self, vehicle_id):
        """
        Wraps a `run_transaction` call that "removes" a vehicle.

        Arguments:
            id {UUID} -- The vehicle's unique ID.
        """
        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: remove_vehicle_txn(session, vehicle_id))

    def add_vehicle(self, vehicle_type, longitude, latitude, battery):
        """
        Wraps a `run_transaction` call that adds a vehicle.

        Arguments:
            vehicle_type {String} -- The type of vehicle.
        """
        return run_transaction(sessionmaker(bind=self.engine),
                               lambda session: add_vehicle_txn(session,
                                                               vehicle_type,
                                                               longitude,
                                                               latitude,
                                                               battery))

    def get_vehicles(self, max_vehicles=None):
        """
        Wraps a `run_transaction` call that gets all vehicle.

        Returns:
            A list of dictionaries containing vehicle data.
        """
        if max_vehicles is None:
            max_vehicles = self.max_records

        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: get_vehicles_txn(session, max_vehicles))

    def get_vehicle(self, vehicle_id):
        """
        Get a single vehicle from its id.
        """
        return run_transaction(sessionmaker(bind=self.engine),
                               lambda session: get_vehicle_txn(session,
                                                               vehicle_id))

    def get_vehicle_and_location_history(self, vehicle_id, max_locations=None):
        """
        Gets vehicle info AND recent locations.

        Inputs
        ------

        vehicle_id (str(uuid)): ID of the vehicle we want
        max_locations (int): Number of points in location_history to show

        Returns
        -------

        (vehicle (dict), location_history (list(dict))):

          vehicle: dictionary representation of the row of the vehicles table
          location_history: list of dictionaries, each representing a row in
              location_history, ordered by timestamp starting at most recent.
        """
        if max_locations is None:
            max_locations = self.max_records

        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: get_vehicle_and_location_history_txn(
                session, vehicle_id, max_locations))

    def show_tables(self):
        """
        Returns:
            List -- A list of tables in the database it's connected to.
        """
        return self.engine.table_names()

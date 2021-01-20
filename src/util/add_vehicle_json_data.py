#!/usr/bin/env python
"""
Update the movr.vehicles table to rewrite the vehicle_info column into JSON.

Usage:
    ./add_vehicle_json_data.py [options]

Options:
    -h --help               Show this text.
    --url <url>             URL given by CockroachCloud.
    -n <num>                Number of prarallel processes to use [default: 30]
"""

import csv
from multiprocessing import Process

from datetime import datetime
from docopt import docopt
import urllib.request
import codecs

import connect_with_sqlalchemy as sqla


def update_row(engine, table_name, primary_key, column_to_update, new_value):
    """
    Performs an update of a row in the database.

    Inputs
    ------
    engine (sqlalchemy.engine.base.Engine): SQLAlchemy engine connected to a
        CockroachDB cluster.
    table_name (string): Name of the table you are updating
    primary_key (string): Representation of the UUID for id of the row.
    column_name (string): Name of the column you're working with.
    new_value (string): String representation of the new value you're adding
        to the row.

    """
    return engine.execute(("UPDATE {table} SET {column} = '{value}' "
                           "WHERE id = '{primary_key_value}'"
                           ).format(table=table_name, column=column_to_update,
                                    primary_key_value=primary_key,
                                    value=new_value))


def import_csv():
    """
    Imports a CSV and returns a dictionary of key: value pairs.

    Inputs
    ------
    filename (str): name of the CSV file. This should be pipe (`|`) delimited
        and include only the Primary Key (in string format) and the JSON data
        you want to add in the new column
    """
    id_to_json = {}

    url = "https://cockroach-university-public.s3.amazonaws.com/10000row_json_column.csv"
    ftpstream = urllib.request.urlopen(url)
    csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'), delimiter='|')

    for row in csvfile:
        id_to_json[row[0]] = row[1]
        
    return id_to_json


def subdivide_dict(dictionary, num_subdivisions):
    """
    Distributes the k: v pairs in dict to N dicts.
    """
    subdicts = [{} for i in range(num_subdivisions)]
    for i, k in enumerate(dictionary.keys()):
        sub_index = i % num_subdivisions
        subdicts[sub_index][k] = dictionary[k]
    return subdicts


def update_csv(one_csv, table_name, column_to_update, sqla_url):
    """
    Updates a column of a dict based on another column.
    """
    engine = sqla.build_engine(sqla_url)
    for k, v in one_csv.items():
        result = update_row(engine, table_name, k, column_to_update, v)


def main():
    opts = docopt(__doc__)

    # Build engine & test
    url = opts['--url']
    sqla_url = sqla.build_sqla_connection_string(url)
    engine = sqla.build_engine(sqla_url)
    sqla.test_connection(engine)

    num_processes = int(opts['-n'])
    # import CSV & update columns
    my_csv = import_csv()
    sub_csvs = subdivide_dict(my_csv, num_processes)
    table_name = "movr.vehicles"
    column_to_update = "vehicle_info"
    processes = []

    # break up the workload among N processes
    for csv_partition in sub_csvs:
        p = Process(target=update_csv, args=(csv_partition, table_name,
                                             column_to_update, sqla_url))
        processes.append(p)
        p.start()

    start_time = datetime.now()
    print("Started at: {}".format(start_time))
    for p in processes:
        p.join()

    end_time = datetime.now()
    print("Ended at: {}".format(end_time))
    duration = end_time - start_time
    print("Total time: {}".format(duration))


if __name__ == '__main__':
    main()

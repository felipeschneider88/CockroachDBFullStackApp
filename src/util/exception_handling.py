"""
Library of functions for capturing/displaying errors in the running web server.
"""

from flask import render_template
from sqlalchemy.exc import IntegrityError


def check_for_missing_table(error, table_name):
    """
    Determines if the error is caused by a missing  table.

    Parses the exception message to determine this.

    Inputs
    ------

    e (ProgrammingError): ProgrammingError exception caught during a query
    table_name (string): Name of the table to check.
    """
    return ('relation "{}" does not exist'.format(table_name) in str(error))


def render_suggestions_for_missing_table(error, movr, table_name):
    """
    Renders 'display_error.html' template for a missing table.
    """
    title = "Cannot load page"
    reason = 'Caught Exception: sqlalchemy.exc.ProgrammingError'
    context = "This occured because there is no `{}` table.".format(table_name)
    possible_sources = ["You may be connected to the wrong database, hence "
                        "the missing table. Your database may not have the "
                        "`{}` table for some reason.".format(table_name),
                        "You may also want to use the `dbinit.sql`"]
    possible_solutions = ["Suggestion: connect with the SQL shell and find "
                          "out if your database is in the correct state."]
    additional_information = {
        "database_connected": movr.engine.url.database,
        "tables_in_database": movr.show_tables(),
        "connection_string": movr.connection_string}

    return render_template('display_error.html',
                           title=title,
                           reason=reason,
                           context=context,
                           possible_sources=possible_sources,
                           possible_solutions=possible_solutions,
                           additional_information=additional_information,
                           exception_text=str(error))


def check_for_wrong_schema(error):
    """
    Checks if column does not exist
    """
    return "UndefinedColumn" in str(error)


def render_suggestions_for_wrong_schema(error, movr):
    """
    Renders error page for when the user attempts a query with the wrong schema
    """
    title = "Cannot load page"
    reason = 'Caught Exception: sqlalchemy.exc.ProgrammingError'
    context = "This occurred because you queried a nonexistent column."
    possible_sources = ["Your database may have a schema that is incompatible "
                        "with the version of MovR you are trying to run."]
    possible_solutions = ["Suggestion: run the `dbinit.sql` script in the "
                          "SQL shell."]

    additional_information = {
        "database_connected": movr.engine.url.database,
        "tables_in_database": movr.show_tables(),
        "connection_string": movr.connection_string}

    return render_template('display_error.html',
                           title=title,
                           reason=reason,
                           context=context,
                           possible_sources=possible_sources,
                           possible_solutions=possible_solutions,
                           additional_information=additional_information,
                           exception_text=str(error))


def render_fk_violation(error, movr):
    title = "Cannot load page"
    reason = ("Caught exception: sqlalchemy.exc.IntegrityError that describes "
              "a Foreign Key violation.")
    context = ("This occurred because the code is inserting a row with a "
               "foreign key constraint and no parent.")
    possible_solutions = [
        ("If you're inserting both the parent and child rows in the same "
         "transaction, you may need to session.flush() after the first."),
        "If not, check where the parent id is coming from in the child table."]

    additional_information = {
        "database_connected": movr.engine.url.database,
        "tables_in_database": movr.show_tables(),
        "connection_string": movr.connection_string}

    return render_template('display_error.html',
                           title=title,
                           reason=reason,
                           context=context,
                           possible_solutions=possible_solutions,
                           additional_information=additional_information,
                           exception_text=str(error))


def render_ride_not_ending(error, movr):
    title = "Cannot load page"
    reason = ("Caught exception: ValueError that says you're dividing by zero"
              "when calculating a velocity.")
    context = ("This probably occurred because MovR thinks that the most "
               "recent entry in the `location_history` table is the same at "
               "the end of the ride as it was at the begining.")
    possible_solutions = [
            ("Verify that you're inserting a new location_history row when "
             "ending your ride, and that it uses func.now() to set its "
             "timestamp.")]

    additional_information = {
        "database_connected": movr.engine.url.database,
        "tables_in_database": movr.show_tables(),
        "connection_string": movr.connection_string}

    return render_template('display_error.html',
                           title=title,
                           reason=reason,
                           context=context,
                           possible_solutions=possible_solutions,
                           additional_information=additional_information,
                           exception_text=str(error))


def render_runtime_error(error, movr):
    title = "Unknown runtime error"
    reason = "Runtime error thrown by unexpected application logic."

    additional_information = {
        "database_connected": movr.engine.url.database,
        "tables_in_database": movr.show_tables(),
        "connection_string": movr.connection_string}
    return render_template('display_error.html', title=title, reason=reason,
                           additional_information=additional_information,
                           exception_text=str(error))


def check_for_foreign_key_violation(error):
    return (isinstance(error, IntegrityError) and
            "violates foreign key constraint" in str(error))


def check_for_ride_not_ending(error):
    return (isinstance(error, ValueError) and
            ("Cannot calculate an average velocity when the timeinterval is 0"
             in str(error)))


def render_error_page(error, movr):
    """
    Used to display an explanation (and suggestions) for the student.

    Call this if you expect a page to run into a particular error, to tell the
        user what to try.

    Inputs
    ------
    e (ProgrammingErro) - Thrown by SQLAlchemy when something is missing
        (like a database or table).
    """
    if check_for_missing_table(error, "vehicles"):
        return render_suggestions_for_missing_table(error, movr, "vehicles")
    if check_for_missing_table(error, "location_history"):
        return render_suggestions_for_missing_table(error, movr,
                                                    "location_history")
    if check_for_foreign_key_violation(error):
        return render_fk_violation(error, movr)
    if check_for_wrong_schema(error):
        return render_suggestions_for_wrong_schema(error, movr)
    if isinstance(error, RuntimeError):
        return render_runtime_error(error, movr)
    if check_for_ride_not_ending(error):
        return render_ride_not_ending(error, movr)

    # We're not expecting this. Gotta give you the stack trace.
    raise error

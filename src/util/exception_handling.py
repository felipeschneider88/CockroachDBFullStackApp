"""
Library of functions for capturing/displaying errors in the running web server.
"""

from flask import render_template


def check_for_missing_vehicles_table(error):
    """
    Determines if the error is caused by a missing "vehicles" table.

    Parses the exception message to determine this.

    Inputs
    ------

    e (ProgrammingError): ProgrammingError exception caught during a query
    """
    return '"vehicles" does not exist' in str(error)


def render_suggestions_for_missing_vehicles_table(error, movr):
    """
    Renders 'display_error.html' template for a missing vehicles table.
    """
    title = "Cannot load page"
    reason = 'Caught Exception: sqlalchemy.exc.ProgrammingError'
    context = "This occured because there is no `vehicles` table."
    possible_sources = ["You may be connected to the wrong database, hence "
                        "the missing table. Your database may not have the "
                        "`vehicles` table for some reason."]
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
    if check_for_missing_vehicles_table(error):
        # This can happen if you haven't run `dbinit.sql`
        return render_suggestions_for_missing_vehicles_table(error, movr)
    if check_for_wrong_schema(error):
        return render_suggestions_for_wrong_schema(error, movr)
    if isinstance(error) is RuntimeError:
        return render_runtime_error(error, movr)

    # We're not expecting this. Gotta give you the stack trace.
    raise error

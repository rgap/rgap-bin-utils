#!/usr/bin/env python3
"""Checks if a PostgreSQL URI can connect successfully.

Usage:
    rgap_checkpguri.py <uri>
    rgap_checkpguri.py <uri> [--query <query>]
    rgap_checkpguri.py -h

Arguments:
    uri     PostgreSQL connection URI

Options:
    --query <query>   SQL query used to test the connection
                      [default: SELECT current_database();]

Examples:
    rgap_checkpguri.py postgresql://postgres:root@localhost:5432/fullstock_dev

    rgap_checkpguri.py postgresql://postgres:root@localhost:5432/fullstock_dev --query "SELECT 1;"

"""

import sys

import psycopg


def main(args):
    uri = args["<uri>"]
    query = args["--query"]

    try:
        # Try to open a connection using the PostgreSQL URI.
        connection = psycopg.connect(uri)

        # Create a cursor to execute a simple SQL query.
        cursor = connection.cursor()

        # Run the test query.
        cursor.execute(query)

        # Get the result of the query.
        result = cursor.fetchone()

        print("Connection successful")
        print(f"URI: {uri}")
        print(f"Test query: {query}")
        print(f"Result: {result}")

        # Close cursor and connection.
        cursor.close()
        connection.close()

    except Exception as error:
        print("Connection failed")
        print(f"URI: {uri}")
        print(f"Error: {error}")

        sys.exit(1)


if __name__ == "__main__":
    # This will only be executed when this module is run directly.
    from docopt import docopt

    main(docopt(__doc__))
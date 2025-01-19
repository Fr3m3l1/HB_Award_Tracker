import bcrypt
import sqlite3 as db
import logging as log
import pandas as pd

# User authentication
async def authenticate_user(username, password) -> dict:
    # Retrieve the user from the database
    user = await get_user(username)
    if user:
        # Verify the password
        if bcrypt.checkpw(password.encode(), user[2].encode()):
            return user
    return None

# Retrieve a user by username
async def get_user(username) -> dict:
    # Query the database for the user
    # Return the user as a dictionary
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    cursor.close()
    data.close()
    return user

# Retrieve QSO data for a user
async def get_qsos(user_id, offset=None, limit=None) -> pd.DataFrame:
    # Query the database for the user's QSO data
    # Return the data as a list of dictionaries
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    cursor.execute('SELECT * FROM qsos WHERE user_id = ?', (user_id,))
    if limit:
        cursor.execute('SELECT * FROM qsos WHERE user_id = ? LIMIT ? OFFSET ?', (user_id, limit, offset))
    qsos = cursor.fetchall()
    cursor.close()
    data.close()

    # Convert the data to a DataFrame
    columns = [col[0] for col in cursor.description]
    qsos = pd.DataFrame(qsos, columns=columns)

    return qsos

async def save_qsos(user_id, df):
    data_path = 'data/db/database.db'
    data = db.connect(data_path)

    # Get the max id from the database
    cursor = data.cursor()
    cursor.execute('SELECT MAX(id) FROM qsos')
    id = cursor.fetchone()[0]
    id = id + 1 if id else 1

    # Delete existing QSOs for the user
    data.execute('DELETE FROM qsos WHERE user_id = ?', (user_id,))
    data.commit()
    log.info(f"Deleted existing QSOs for user {user_id}")

    # Insert each QSO into the database
    try:
        for index, row in df.iterrows():
            data.execute('''
                INSERT INTO qsos (
                    id, user_id, CALL, BAND, MODE, TIME_ON, TIME_OFF, FREQ, COUNTRY, DISTANCE, EMAIL,
                    EQSL_QSLRDATE, EQSL_QSLSDATE, LOTW_QSLRDATE, LOTW_QSLSDATE, QSLRDATE, QSLSDATE, GRIDSQUARE, LAT, LON,
                    ANT_AZ, ANT_EL, CONT, DXCC, FORCE_INIT, K_INDEX, PFX, QSO_COMPLETE, QSO_RANDOM, RST_RCVD, RST_SENT,
                    RX_PWR, SFI, STATION_CALLSIGN, SWL, TX_PWR, QSO_DATE
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                id, user_id, row['CALL'], row['BAND'], row['MODE'], row['TIME_ON'], row['TIME_OFF'], row['FREQ'],
                row['COUNTRY'], row['DISTANCE'], row['EMAIL'], row['EQSL_QSLRDATE'], row['EQSL_QSLSDATE'], row['LOTW_QSLRDATE'],
                row['LOTW_QSLSDATE'], row['QSLRDATE'], row['QSLSDATE'], row['GRIDSQUARE'], row['LAT'], row['LON'],
                row['ANT_AZ'], row['ANT_EL'], row['CONT'], row['DXCC'], row['FORCE_INIT'], row['K_INDEX'], row['PFX'],
                row['QSO_COMPLETE'], row['QSO_RANDOM'], row['RST_RCVD'], row['RST_SENT'], row['RX_PWR'], row['SFI'],
                row['STATION_CALLSIGN'], row['SWL'], row['TX_PWR'], row['QSO_DATE']
            ))
            id += 1

        # Commit the transaction and close the connection
        data.commit()
        log.info(f"Saved {len(df)} QSOs for user {user_id}")
    except Exception as e:
        print(f"Error saving QSOs: {e}")
    data.close()


# Load the awards for a user
async def load_awards(user_id):
    # Query the database for the user's awards
    # Return the data as a list of dictionaries
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    cursor.execute('''
        SELECT * FROM awards WHERE user_id = ?
    ''', (user_id,))
    awards = cursor.fetchall()
    cursor.close()
    data.close()
    return awards

# Save an award for a user
async def save_award(user_id, name, query, filter, count=0, start_date=None, end_date=None, query_text=None):
    # Save the award to the database
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()

    print(f"Query Text: {query_text}")

    # Get the max id from the database
    cursor.execute('SELECT MAX(id) FROM awards')
    id = cursor.fetchone()[0]
    id = id + 1 if id else 1

    cursor.execute('''
        INSERT INTO awards (id, user_id, award_name, award_query, award_query_text, award_filter, award_count, award_start_date, award_end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id, user_id, name, query, query_text, filter, count, start_date, end_date))
    data.commit()
    cursor.close()
    data.close()
    log.info(f"Saved award {name} for user {user_id}")

# Update an award for a user
async def update_award(user_id, award):
    # Update the award in the database
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    cursor.execute('''
        UPDATE awards
        SET name = ?, description = ?, date = ?
        WHERE id = ?
    ''', (award['name'], award['description'], award['date'], award['id']))
    data.commit()
    cursor.close()
    data.close()
    log.info(f"Updated award {award['name']} for user {user_id}")

# Delete an award for a user
async def delete_award(award_id):
    # Delete the award from the database
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    cursor.execute('''
        DELETE FROM awards
        WHERE id = ?
    ''', (award_id,))
    data.commit()
    cursor.close()
    data.close()
    log.info(f"Deleted award {award_id}")


def create_query(user_id, grouping=None, counter="DXCC", filter=None, filter_query=None):
    """
    Creates an SQL query to count unique DXCC values based on specified groupings.

    Args:
        user_id (int): The ID of the user for whom to generate the query.
        grouping (str, list, or None): Specifies the grouping for the query.
            Possible values:
            - 'BAND': Group by band.
            - 'MODE': Group by mode.
            - ['MODE', 'BAND'] or ['BAND', 'MODE']: Group by mode and band.
            - None: No grouping, count unique DXCC overall.
        counter (str): The column representing the DXCC value (default: "DXCC").

    Returns:
        str: The generated SQL query.

    Raises:
        ValueError: If an invalid grouping value is provided.
    """

    valid_groupings = ['BAND', 'MODE', 'COUNTRY']

    # Decode the grouping parameter and create the query
    split_grouping = grouping.split(',')
    if len(split_grouping) > 1:
        grouping = split_grouping
        # remove any whitespace
        grouping = [item.strip() for item in grouping]

    if grouping == "":
        grouping = None
        # Count unique DXCC overall (no grouping)
        query = f"SELECT COUNT(DISTINCT {counter}) AS total_unique_dxcc FROM qsos WHERE user_id = {user_id}"

    elif isinstance(grouping, str) and grouping in valid_groupings:
        # Group by a single attribute (BAND or MODE)
        query = f"""
            SELECT 
                {grouping}, 
                COUNT(DISTINCT {counter}) AS unique_dxcc_per_{grouping}
            FROM qsos 
            WHERE user_id = {user_id} {f" AND {filter_query}" if filter_query else ""}
            GROUP BY {grouping}
            """

    elif isinstance(grouping, list) and all(item in valid_groupings for item in grouping) and len(grouping) == 2:
        # Group by two attributes (MODE and BAND)
        query = f"""
            SELECT 
                {grouping[0]}, 
                {grouping[1]}, 
                COUNT(DISTINCT {counter}) AS unique_dxcc_per_{grouping[0]}_{grouping[1]}
            FROM qsos 
            WHERE user_id = {user_id} {f" AND {filter_query}" if filter_query else ""}
            GROUP BY {grouping[0]}, {grouping[1]}
            """

    else:
        print(f"Invalid grouping: {grouping}. "
                         f"Valid groupings are: {valid_groupings}, a combination of them, or None.")
        return None
    
    if type(grouping) == str:
        grouping = [grouping]

    return [query, grouping]

# Get the results of an award query
async def get_award_query_results(user_id, query, filter_query=None):

    query, columns = create_query(user_id, query, filter_query=filter_query)

    # Query the database for the results of an award query
    # Return the data as a list of dictionaries
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        results = -1
    cursor.close()
    data.close()
    return [results, columns]

async def get_country_list(user_id):
    # Query the database for the user's awards
    # Return the data as a list of dictionaries
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    #Sort the countries by name
    cursor.execute('''
        SELECT DISTINCT COUNTRY FROM qsos WHERE user_id = ?
        ORDER BY COUNTRY
    ''', (user_id,))
    countries = cursor.fetchall()
    cursor.close()
    data.close()
    return countries
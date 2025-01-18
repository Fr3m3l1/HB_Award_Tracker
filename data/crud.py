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
async def get_qsos(user_id) -> pd.DataFrame:
    # Query the database for the user's QSO data
    # Return the data as a list of dictionaries
    # Mage db connection
    data = db.connect('data/db/database.db')
    cursor = data.cursor()
    cursor.execute('SELECT * FROM qsos WHERE user_id = ?', (user_id,))
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

    # Delete existing QSOs for the user
    data.execute('DELETE FROM qsos WHERE user_id = ?', (user_id,))
    data.commit()
    log.info(f"Deleted existing QSOs for user {user_id}")

    # Insert each QSO into the database
    try:
        for index, row in df.iterrows():
            data.execute('''
                INSERT INTO qsos (
                    user_id, CALL, BAND, MODE, TIME_ON, TIME_OFF, FREQ, COUNTRY, DISTANCE, EMAIL,
                    EQSL_QSLRDATE, EQSL_QSLSDATE, LOTW_QSLRDATE, LOTW_QSLSDATE, QSLRDATE, QSLSDATE, GRIDSQUARE, LAT, LON,
                    ANT_AZ, ANT_EL, CONT, DXCC, FORCE_INIT, K_INDEX, PFX, QSO_COMPLETE, QSO_RANDOM, RST_RCVD, RST_SENT,
                    RX_PWR, SFI, STATION_CALLSIGN, SWL, TX_PWR, QSO_DATE
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                user_id, row['CALL'], row['BAND'], row['MODE'], row['TIME_ON'], row['TIME_OFF'], row['FREQ'],
                row['COUNTRY'], row['DISTANCE'], row['EMAIL'], row['EQSL_QSLRDATE'], row['EQSL_QSLSDATE'], row['LOTW_QSLRDATE'],
                row['LOTW_QSLSDATE'], row['QSLRDATE'], row['QSLSDATE'], row['GRIDSQUARE'], row['LAT'], row['LON'],
                row['ANT_AZ'], row['ANT_EL'], row['CONT'], row['DXCC'], row['FORCE_INIT'], row['K_INDEX'], row['PFX'],
                row['QSO_COMPLETE'], row['QSO_RANDOM'], row['RST_RCVD'], row['RST_SENT'], row['RX_PWR'], row['SFI'],
                row['STATION_CALLSIGN'], row['SWL'], row['TX_PWR'], row['QSO_DATE']
            ))

        # Commit the transaction and close the connection
        data.commit()
        log.info(f"Saved {len(df)} QSOs for user {user_id}")
    except Exception as e:
        print(f"Error saving QSOs: {e}")
    data.close()

import sqlite3 as db
import bcrypt

# initialze the database
def init_db():
    data_path = 'data/db/database.db'
    data = db.connect(data_path)

    # Create the users table
    data.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the qsos table with additional columns
    data.execute('''
        CREATE TABLE IF NOT EXISTS qsos (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            CALL TEXT NOT NULL,
            BAND TEXT,
            MODE TEXT,
            TIME_ON TEXT,
            TIME_OFF TEXT,
            FREQ TEXT,
            COUNTRY TEXT,
            DISTANCE FLOAT,
            EMAIL TEXT,
            EQSL_QSLRDATE TEXT,
            EQSL_QSLSDATE TEXT,
            LOTW_QSLRDATE TEXT,
            LOTW_QSLSDATE TEXT,
            QSLRDATE TEXT,
            QSLSDATE TEXT,
            GRIDSQUARE TEXT,
            LAT FLOAT,
            LON FLOAT,
            ANT_AZ FLOAT,
            ANT_EL FLOAT,
            CONT TEXT,
            DXCC INTEGER,
            FORCE_INIT TEXT,
            K_INDEX FLOAT,
            PFX TEXT,
            QSO_COMPLETE TEXT,
            QSO_RANDOM TEXT,
            RST_RCVD TEXT,
            RST_SENT TEXT,
            RX_PWR FLOAT,
            SFI FLOAT,
            STATION_CALLSIGN TEXT,
            SWL TEXT,
            TX_PWR FLOAT,
            QSO_DATE TEXT
        )
    ''')

    # Create an index on the user_id column
    data.execute('''
        CREATE INDEX IF NOT EXISTS user_id_index ON qsos (user_id)
    ''')

    # Create the awards table with autoincrementing id
    data.execute('''
        CREATE TABLE IF NOT EXISTS awards (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            award_name TEXT NOT NULL,
            award_query TEXT
        )
    ''')

    # Create an index on the user_id column
    data.execute('''
        CREATE INDEX IF NOT EXISTS user_id_awards_index ON awards (user_id)
    ''')

    crypt_salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw('PQK0cbk@bpu4uez2kat'.encode(), crypt_salt)

    # Create a user if it does not exist
    if not data.execute('SELECT * FROM users WHERE username = ?', ('fr3m3l@gmail.com',)).fetchone():
        data.execute(f'''
            INSERT INTO users (id, username, password) VALUES (1, 'fr3m3l@gmail.com', '{hashed_password.decode()}')
        ''')

    hashed_password = bcrypt.hashpw('1234'.encode(), crypt_salt)

    if not data.execute('SELECT * FROM users WHERE username = ?', ('Ernst',)).fetchone():
        data.execute(f'''
            INSERT INTO users (id, username, password) VALUES (2, 'Ernst', '{hashed_password.decode()}')
        ''')

    # Commit the transaction
    data.commit()
    # Close the connection
    data.close()
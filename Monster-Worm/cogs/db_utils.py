import logging 
import sqlite3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask.app").setLevel(logging.ERROR)

def db_init():
    """
    Creates a new database file if it doesn't exists and then runs the
    create_tables function.
    """
    try:
        con = sqlite3.connect("bot.db")
        logging.info("Connected to the database.")
        create_tables(con)
        return con
    except sqlite3.Error as e:
        logging.error("Error initializing database.")
        return None

def create_tables(con):
    """
    It is executed for every connection to the database to verify and repair any inconsitencies in the database,
    It creates a missing table if it doesn't exists.
    """
    try:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                osint_bot_channel INTEGER,
                activity_music_bot_channel INTEGER,
                lightshot_bot_channel INTEGER,
                nmap_bot_channel INTEGER,
                whostared_bot_channel INTEGER
            )
        """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS message_backup (
                times_tamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_name TEXT,
                message TEXT

            )
        """
        )

    except sqlite3.Error as e:
        logging.error(f"Error creating tables: {e}")

def update_config(con, key: str, value: int):
    """
    Updates the config table of the database, As this bot is made for single server use only,
    We use the id 0, to effectively update each attribute of the table independently.
    """
    try:
        cur = con.cursor()

        # Check if the record with id = 0 exists
        cur.execute("SELECT id FROM config WHERE id = 0")
        existing_record = cur.fetchone()

        if existing_record:
            # Update the existing record
            query = f"UPDATE config SET {key} = ? WHERE id = 0"
            cur.execute(query, (value,))
        else:
            # Insert a new record with id = 0
            query = f"INSERT INTO config (id, {key}) VALUES (0, ?)"
            cur.execute(query, (value,))

        con.commit()
        logging.info("Updated table config successfully.")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error updating table config: {e}")
        return False

def fetch_config(con):
    """
    A function which is used to return all the records and return it as dictionary,
    if their is no config then it returns False.
    """
    try:
        cur = con.cursor()

        cur.execute("SELECT * FROM config")
        row = cur.fetchone()
        if row:
            return {
                "osint_bot_channel": row[1],
                "activity_music_bot_channel": row[2],
                "lightshot_bot_channel": row[3],
                "nmap_bot_channel": row[4],
                "whostared_bot_channel": row[5]
            }
    except sqlite3.Error as e:
        logging.error(f"Error fetching table config: {e}")
        return None

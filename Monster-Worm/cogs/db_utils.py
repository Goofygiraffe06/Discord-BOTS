import logging 
import sqlite 

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask.app").setLevel(logging.ERROR)

def db_init():
    """
    Creates a new database file if it doesn't exists and then runs the create_tables function.
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
            CREATE TABLE IF NOT EXISTS challenge_data (
                times_tamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_name TEXT,
                message TEXT

            )
        """
        )

    except sqlite3.Error as e:
        logging.error(f"Error creating tables: {e}")


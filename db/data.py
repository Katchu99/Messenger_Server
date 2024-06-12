import mysql.connector
import logging
from mysql.connector import errorcode
from datetime import datetime

logger = logging.getLogger(__name__)

class chatData():
    def __init__(self, host, user, password, database) -> None:
        #MySQL Parameters
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.curesor = None

        self.connect()
        logger.info(f"Initialized chatData with host ={host}, user={user}, database={database}")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password = self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to the database")
            # self.create_user_table()
            # self.create_chat_table()
            # self.create_friends_table()
        except mysql.connector.errors.DatabaseError as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(f"MySQL-Database {self.database} does not exist. Creating database...")
                self.create_database()
                self.connect()
            else:
                logger.exception(f"Database connection error: {err}")
                raise

    def create_database(self):
        try:
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            temp_cursor = temp_connection.cursor()
            logger.info(f"Successfully established temporary connection for MySQL database creation.")
            temp_cursor.execute('''CREATE DATABASE IF NOT EXISTS mawi''')
            temp_connection.commit()
            temp_cursor.close()
            temp_connection.close()
            logger.info(f"MySQL-Database {self.database} created successfully.")
        except mysql.connector.Error as err:
            logger.exception(f"Error creating database: {err}")
            raise
     
data_obj = chatData(
    host="localhost",
    user="server",
    password="rootroot",
    database="mawi"
)
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
        self.cursor = None

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
            self.create_user_table()
            self.create_chat_table()
            self.create_friends_table()
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

    def create_user_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id VARCHAR(255) PRIMARY KEY,
                                username VARCHAR(255),
                                password VARCHAR(255)
            )''')

        self.connection.commit()
        logger.info("User table created or already exists.")

    def create_chat_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                name TEXT,
                                chat_member_ids JSON,
                                chat_content_id VARCHAR(255)
                                )''')
            
        self.connection.commit()
        logger.info("Chat table created or already exists.")

    def create_friends_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS friends (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                userid1 INT,
                                userid2 INT,
                                status VARCHAR(50))''')
            
        self.connection.commit()
        logger.info("Friends table created or already exists.")

data_obj = chatData(
    host="localhost",
    user="root",
    password="rootroot",
    database="mawi"
)
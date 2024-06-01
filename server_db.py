import mysql.connector
import bcrypt
import logging
from mysql.connector import errorcode
from datetime import datetime

# Initialize Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='db.log',
    filemode='w'
)

# Initliaze Logger for this Module
logger = logging.getLogger(__name__)


class chatDB():
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.connect()
        logger.info(f"Initialized chatDB with host={host}, user={user}, database={database}")

    def connect(self):
        try:
            self.connection = mysql.connector.connect( 
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to the database.")
            self.create_user_table()
            self.create_chat_table()
            self.create_friends_table()
        except mysql.connector.errors.DatabaseError as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(f"Database {self.database} does not exist.\nCreating database...")
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
            logger.info(f"Successfully established temporary connection for database creation.")
            temp_cursor.execute('''CREATE DATABASE IF NOT EXISTS mawi''')
            temp_connection.commit()
            temp_cursor.close()
            temp_connection.close()
            logger.info(f"Database {self.database} created successfully.")
        except mysql.connector.Error as err:
            logger.exception(f"Error creating database: {err}")
            raise

    def create_user_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255),
                            password VARCHAR(255)
        )''')

        self.connection.commit()
        logger.info("User table created or already exists.")

    def create_chat_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            sender VARCHAR(255),
                            receiver VARCHAR(255),
                            message TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def check_if_exists(self, username):
        sql = '''SELECT username FROM users WHERE username=%s'''
        values = (username,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchone()
        exists = result is not None
        logger.debug(f"Check if user exists ({username}): {exists}")
        return exists

    def get_id_by_name(self, username):
        sql = '''SELECT id FROM users
                WHERE username=%s'''
        values = (username,)
        self.cursor.execute(sql, values)
        user_id = self.cursor.fetchone()
        logger.debug(f"Get ID by username ({username}): {user_id}")
        return user_id

    def get_name_by_id(self, user_id):
        sql = '''SELECT username FROM users
                WHERE id = %s'''
        values = (user_id,)
        self.cursor.execute(sql, values)
        username = self.cursor.fetchone()
        logger.debug(f"Get username by ID ({user_id}): {username}")
        return username

    def register_user(self, username, password):
        if not self.check_if_exists(username):
            sql = '''INSERT INTO users (username, password) VALUES (%s, %s)'''
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            values = (username, hashed_password)
            self.cursor.execute(sql, values)
            self.connection.commit()
            logger.info(f"User {username} registered successfully.")
            return "Successful"
        else:
            logger.warning(f"Attempt to register taken username: {username}")
            return "Username already taken!"

    def authenticate_user(self, username, password):
        sql = '''SELECT password FROM users WHERE username=%s'''
        values = (username, )
        self.cursor.execute(sql, values)
        hashed_password = self.cursor.fetchone()[0]
        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            logger.info(f"User {username} authenticated successfully.")
            return True
        else:
            logger.warning(f"Failed authentication attempt for user: {username}")
            return False

    def add_message(self, sender, receiver, message):
        sql = '''INSERT INTO chats (sender, receiver, message)
                        VALUE (%s, %s, %s)'''
        
        values = (sender, receiver, message)
        self.cursor.execute(sql, values)
        self.connection.commit()
        logger.info(f"Message from {sender} to {receiver} added to chat.")

    def get_message(self, sender, receiver):
        sql = '''SELECT sender, message, timestamp FROM chats
                    WHERE (sender=%s AND receiver=%s) OR (sender=%s AND receiver=%s)
                    ORDER BY timestamp'''
        values = (sender, receiver, receiver, sender)
        self.cursor.execute(sql, values)
        messages = self.cursor.fetchall()
        logger.debug(f"Retrieved messages between {sender} and {receiver}.")
        return messages

    def get_global_message_history(self):
        sql = '''SELECT sender, message, timestamp FROM chats
                WHERE receiver="global"
                ORDER BY timestamp'''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        formatted_result = []

        for row in result:
            message = {
            'username': '',
            'text': ''
            }

            row = list(row)
            message['username'] = row[0]
            message['text'] = row[1]
            formatted_result.append(message)

        logger.debug("Retrieved global message history.")
        return formatted_result

    def send_friend_request(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''INSERT INTO friends (userid1, userid2, status)
                VALUES (%s, %s, %s)'''
        values = (sender_id, receiver_id, "pending")
        self.cursor.execute(sql, values)
        self.connection.commit()
        logger.info(f"Friend request sent from {sender} to {receiver}.")

    def accept_friend_request(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''UPDATE friends SET status = %s
                WHERE userid1 = %s AND userid2 = %s AND status=%s OR
                userid1 = %s AND userid2 = %s AND status=%s'''
        values = ("accepted", sender_id, receiver_id, "pending", receiver_id, sender_id, "pending")
        self.cursor.execute(sql, values)
        self.connection.commit()
        logger.info(f"Friend request accepted between {sender} and {receiver}.")

    def reject_friend_request(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''UPDATE friends SET status = %s
                WHERE userid1 = %s AND userid2 = %s AND status=%s OR
                userid1 = %s AND userid2 = %s AND status=%s'''
        values = ("rejected", sender_id, receiver_id, "pending", receiver_id, sender_id, "pending")
        self.cursor.execute(sql, values)
        self.connection.commit()
        logger.info(f"Friend request rejected between {sender} and {receiver}.")
    
    def get_friends(self, sender):
        sender_id = self.get_id_by_name(sender)
        sql = '''SELECT userid1, userid2 FROM friends
                WHERE (userid1 = %s OR userid2 = %s) AND status = %s'''
        values = (sender_id, sender_id, "accepted")
        self.cursor.execute(sql, values)

        friends = []
        for row in self.cursor.fetchall():
            friend_id = row[0] if row[0] != sender_id else row[1]
            friends.append(self.get_name_by_id(friend_id))
        
        logger.debug(f"Retrieved friends list for {sender}.")
        return friends
    
    def remove_friend(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''DELETE FROM friends
                WHERE (userid1 = %s AND userid2 = %s) OR (userid1 = %s AND userid2 = %s)'''
        values = (sender_id, receiver_id, receiver_id, sender_id)
        self.cursor.execute(sql, values)
        self.connection.commit()
        logger.info(f"Friendship removed between {sender} and {receiver}.")
        
    def close(self):
        self.connection.close()

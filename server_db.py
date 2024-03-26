import mysql.connector
import bcrypt
from mysql.connector import errorcode
from datetime import datetime

class chatDB():
    def __init__(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect( 
                host=host,
                user=user,
                password=password,
                database=database
            )
        except mysql.connector.errors.DatabaseError as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Database {database} does not exist.\nCreating database...")
                self.create_database()
            else:
                print("Error:", err)

        self.cursor = self.connection.cursor()
        self.create_user_table()
        self.create_chat_table()
        self.create_friends_table()

    def create_database(self, host, user, password):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor.execute('''CREATE DATABASE IF NOT EXISTS mawi''')
        self.connection.commit()
        self.cursor.execute('''USE mawi''')
        self.connection.commit()

    def create_user_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255),
                            password VARCHAR(255)
        )''')

        self.connection.commit()

    def create_chat_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            sender VARCHAR(255),
                            receiver VARCHAR(255),
                            message TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
        
        self.connection.commit()

    def create_friends_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS friends (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            userid1 INT,
                            userid2 INT,
                            status VARCHAR(50))''')
        
        self.connection.commit()

    def check_if_exists(self, username):
        sql = '''SELECT username FROM users WHERE username=%s'''
        values = (username,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def get_id_by_name(self, username):
        sql = '''SELECT id FROM users
                WHERE username=%s'''
        values = (username,)
        self.cursor.execute(sql, values)
        return self.cursor.fetchone()

    def get_name_by_id(self, user_id):
        sql = '''SELECT username FROM users
                WHERE id = %s'''
        values = (user_id,)
        self.cursor.execute(sql, values)
        return self.cursor.fetchone()

    def register_user(self, username, password):
        if not self.check_if_exists(username):
            sql = '''INSERT INTO users (username, password) VALUES (%s, %s)'''
            values = (username, password)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return "Successful"
        else:
            return "Username already taken!"

    def authenticate_user(self, username, password):
        sql = '''SELECT password FROM users WHERE username=%s'''
        values = (username, )
        self.cursor.execute(sql, values)
        hashed_password = self.cursor.fetchone()
        print(hashed_password)
        if hashed_password:
            return bcrypt.checkpw(hashed_password[0].encode('utf-8'), password.encode('utf-8'))
        return False

    def add_message(self, sender, receiver, message):
        sql = '''INSERT INTO chats (sender, receiver, message)
                        VALUE (%s, %s, %s)'''
        
        values = (sender, receiver, message)
        self.cursor.execute(sql, values)
        self.connection.commit()

    def get_message(self, sender, receiver):
        sql = '''SELECT sender, message, timestamp FROM chats
                    WHERE (sender=%s AND receiver=%s) OR (sender=%s AND receiver=%s)
                    ORDER BY timestamp'''
        values = (sender, receiver, receiver, sender)
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

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

        return formatted_result

    def send_friend_request(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''INSERT INTO friends (userid1, userid2, status)
                VALUES (%s, %s, %s)'''
        values = (sender_id, receiver_id, "pending")
        self.cursor.execute(sql, values)
        self.connection.commit()

    def accept_friend_request(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''UPDATE friends SET status = %s
                WHERE userid1 = %s AND userid2 = %s AND status=%s OR
                userid1 = %s AND userid2 = %s AND status=%s'''
        values = ("accepted", sender_id, receiver_id, "pending", receiver_id, sender_id, "pending")
        self.cursor.execute(sql, values)
        self.connection.commit()

    def reject_friend_request(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''UPDATE friends SET status = %s
                WHERE userid1 = %s AND userid2 = %s AND status=%s OR
                userid1 = %s AND userid2 = %s AND status=%s'''
        values = ("rejected", sender_id, receiver_id, "pending", receiver_id, sender_id, "pending")
        self.cursor.execute(sql, values)
        self.connection.commit()
    
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
        return friends
    
    def remove_friend(self, sender, receiver):
        sender_id = self.get_id_by_name(sender)
        receiver_id = self.get_id_by_name(receiver)
        sql = '''DELETE FROM friends
                WHERE (userid1 = %s AND userid2 = %s) OR (userid1 = %s AND userid2 = %s)'''
        values = (sender_id, receiver_id, receiver_id, sender_id)
        self.cursor.execute(sql, values)
        self.connection.commit()
        
    def close(self):
        self.connection.close()

# import sqlite3
import os
import psycopg2
import psycopg2.extras
import urllib.parse

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

class SongDB:
    def __init__(self):

        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        # self.connection = sqlite3.connect("songs_db.db")
        # self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()
        
    def __del__(self):
        self.connection.close()

    def createSongsTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS library (id SERIAL PRIMARY KEY, name VARCHAR(255), band VARCHAR(255), rating VARCHAR(255), plays VARCHAR(255))")
        self.connection.commit()


    def insertSong(self, s_name, b_name, rating):
        #insert record into the database
        data = [s_name, b_name, rating, "0"]
        self.cursor.execute("INSERT INTO library (name, band, rating, plays) VALUES (%s, %s, %s, %s)", data)
        self.connection.commit()

    def getAllSongs(self):
        #read from the table
        self.cursor.execute("SELECT * FROM library")
        songs = self.cursor.fetchall() 
        # print(songs, "songs from database, printing from library.py - getAllSongs Method")
        return songs

    def getOneSong(self, song_id):
        data = [song_id]
        self.cursor.execute("SELECT * FROM library WHERE id = %s", data)
        return self.cursor.fetchone()

    def updateSong(self, name, band, rating, plays, id):
        data = [name, band, rating, plays, id]
        self.cursor.execute("UPDATE library SET name = %s, band = %s, rating = %s, plays = %s WHERE id = %s", data)
        self.connection.commit()

    def deleteSong(self, id):
        data = [id]
        self.cursor.execute("DELETE FROM library WHERE id = %s", data)
        self.connection.commit()




    



    ############################
    ##    USERS     ###

    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
        self.connection.commit()




    def createUser(self, username, password):
        data = [username, password]
        udata = [username]
        self.cursor.execute("SELECT username FROM users where username = %s", udata)
        user = self.cursor.fetchone()
        print("this is what returns from the db when creating user.", user)
        if user is None:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", data)
            self.connection.commit()
            print("db helper has received request and the username received is:", username, "and the password is:", password)
            return True
        else:
            print("the create user function in the db helper thinks that the user already exists.")
            return False


    def getUserPassword(self, username):
        data = [username]
        self.cursor.execute("SELECT username FROM users where username = %s", data)
        user = self.cursor.fetchone()
        if user is not None:
            self.cursor.execute("SELECT password FROM users WHERE username = %s", data)
            password = self.cursor.fetchone()
            print("Im getting the password for", user, "its", password)
            return password
        else:
            return False

    def getUser(self, username):
        data = [username]
        self.cursor.execute("SELECT * FROM users where username = %s", data)
        user = self.cursor.fetchone()
        return user






#--------------------#
#      SESSIONS      #
#--------------------#

    # def createSession(self, username)



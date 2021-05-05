from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
from urllib.parse import parse_qs
# from dummydb import DummyDB
from song_list_db import SongDB
from passlib.hash import bcrypt
from http import cookies 
from session_store import SessionStore


gSessionStore = SessionStore()
db = SongDB()



class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_cookie()
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        BaseHTTPRequestHandler.end_headers(self)

    #create a cookie object and save it into self.cookie
    def load_cookie(self):
        #read header
        #capture cookie if one exists
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        # or create one if one doesn't exist.
        else:
            self.cookie = cookies.SimpleCookie()
        

    def send_cookie(self):
        for morsel in self.cookie.values():
        #write header
        #sending cookie data if there is any data.
            self.send_header("Set-Cookie", morsel.OutputString())
        
    def load_session(self):
        #first load the cookie
        self.load_cookie()
        #load session id from the cookie if it exists
        if "sessionId" in self.cookie:
            #use the session id to load the session data from the session store
            sessionId = self.cookie["sessionId"].value
            self.sessionData = gSessionStore.getSessionData(sessionId)
            if self.sessionData == None:
                print("self.sessionData = None!")
                sessionId = gSessionStore.createSession()
                self.sessionData = gSessionStore.getSessionData(sessionId)
                self.cookie["sessionId"] = sessionId
        else:
            print("SessionId is not in Self.cookie!")
            sessionId = gSessionStore.createSession()
            self.sessionData = gSessionStore.getSessionData(sessionId)
            self.cookie["sessionId"] = sessionId
            print("now we created sessionId ")
        #if it doesn't exist create a new session.
        #if the session doesn't exist in the session store
        

    def handleNotFound(self):
        self.send_response(404)
        # self.send_header("Access-Control-Allow-Credentials", "true")
        # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.end_headers()
        # self.send_header("Content-Type", "text/plain")
        # self.end_headers()
        # self.wfile.write(bytes("Not Found", "utf-8"))
        
    def handleSongRetrieveMember(self, id):
        if "userId" not in self.sessionData:
            self.send_response(401)
            self.end_headers
            return
        db = SongDB()
        song = db.getOneSong(id)
        if song:
            self.send_response(200) #<- status code
            # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(song), "utf-8"))
        else:
            self.handleNotFound()




    def handleSongRetrieveCollection(self):
        #ENFORCE AUTHORIZATION (user is not logged in)
        if "userId" not in self.sessionData:
            print("userid was not in self.sessionData in the songretrievecollection function")

            self.send_response(401)
            self.end_headers()
            return        
        


        self.send_response(200) #<- status code
        # headers go here
        # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Content-Type", "application/json")
        self.end_headers()

            #body goes here
        db = SongDB()
        self.wfile.write(bytes(json.dumps(db.getAllSongs()), "utf-8"))

    def handleSongCreate(self):
        if "userId" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            return
        #capture data from the body, and save it:
        #1. read the raw data from the body
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        # print("The Raw body: ", body)

        #2. parse the raw data into usable data
        parsed_body = parse_qs(body)
        # print("The Parsed body:", parsed_body)
        #3. save the data into our array
        name = parsed_body["name"][0]
        band = parsed_body["band"][0]
        rating = parsed_body["rating"][0]
        # songs.append(name)
        db.insertSong(name, band, rating)


        self.send_response(201)
        # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.end_headers()

    def handleSongDeleteMember(self, id):
        if "userId" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            return
        db = SongDB()
        song = db.getOneSong(id)
        if song:
            self.send_response(200) #<- status code
            # headers go here
            # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            db.deleteSong(id)
        else:
            self.handleNotFound()

        

    def handleSongUpdateMember(self, songId):
        if "userId" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            return

        db = SongDB()
        song = db.getOneSong(songId)
        if song:
            # self.wfile.write(bytes(json.dumps(song), "utf-8"))
            #1. read the raw data from the body
            length = self.headers["Content-Length"]
            body = self.rfile.read(int(length)).decode("utf-8")
            # print("The Raw body: ", body)

            #2. parse the raw data into usable data
            parsed_body = parse_qs(body)
            # print("The Parsed body:", parsed_body)
            #3. save the data into our array
            name = parsed_body["name"][0]
            band = parsed_body["band"][0]
            rating = parsed_body["rating"][0]
            plays = parsed_body["plays"][0]
            # identifier = parsed_body["id"][0]
            # songs.append(name)
            db.updateSong(name, band, rating, plays, songId)
            self.send_response(200) #<- status code
            # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
            self.send_header("Content-Type", "application/json")
            self.end_headers()
        else:
            self.handleNotFound()
            
        

    def handleUserCreate(self):
        #capture data from the body, and save it:
        #1. read the raw data from the body
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        # print("The Raw body: ", body)

        #2. parse the raw data into usable data
        parsed_body = parse_qs(body)
        # print("The Parsed body:", parsed_body)
        #3. save the data into our array
        username = parsed_body["username"][0]
        password = parsed_body["password"][0]
        # print("username is:", username, "password is:", password)

        encrypted_password = bcrypt.hash(password)
        new = db.createUser(username, encrypted_password)
        print("This is what the server received back when asking the db helpers to create a user:", new)
        if new is True:
            print("Registration Successful")
            self.send_response(201)
            # self.send_header("Access-Control-Allow-Credentials", "true")
            # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
            self.end_headers()
            # self.send_header("Access-Control-Allow-Origin", "*")
            # self.end_headers()
        else:
            print("Registration: Username already exists")
            self.send_response(422)
            # self.send_header("Access-Control-Allow-Credentials", "true")
            # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
            self.end_headers()
            # self.send_header("Access-Control-Allow-Origin", "*")
            # self.send_header("Content-Type", "text/plain")
            # self.end_headers()
            # self.wfile.write(bytes("User Exists", "utf-8"))

        
    def handleSessionCreate(self):
        #capture data from the body, and save it:
        #1. read the raw data from the body
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")

        #2. parse the raw data into usable data
        parsed_body = parse_qs(body)

        #3. save the data into our array
        username = parsed_body["username"][0]
        password = parsed_body["password"][0]
        # print("username is:", username, "password is:", password)

        # encrypted_password = bcrypt.hash(password)
        Verify = db.getUserPassword(username)
        # user = db.getUser(username)
        if Verify is not False:
            compare = bcrypt.verify(password, Verify["password"])
            if compare is True:
                print("Login Successful")
                self.send_response(201)
                # self.send_header("Access-Control-Allow-Credentials", "true")
                # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
                self.end_headers()
                #SAVE USERS ID INTO SESSION DATA
                self.sessionData["userId"] = username #TODO: GET THE ID TO SAVE INTO THIS
                print("sessionData", self.sessionData)

            else:
                print("Password failed")
                self.handleNotFound()
        else:
            print("User not Found in DB") 
            self.handleNotFound()




    def do_OPTIONS(self):
        self.load_session()
        self.send_response(200)
        # self.send_header("Access-Control-Allow-Origin",self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods","OPTIONS, GET, POST, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()

    
    def do_GET(self):
        self.load_session()
        print("GET request received, now what? Path is: " + self.path)
        path_parts = self.path.split("/")
        resource = path_parts[1]

        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None


        if resource == "songs" and identifier == None:
            self.handleSongRetrieveCollection()

        elif resource == "songs" and identifier != None:
            self.handleSongRetrieveMember(identifier)

        else:
            self.handleNotFound()

    def do_POST(self):
        self.load_session()
        if self.path == "/songs":
            self.handleSongCreate()
        elif self.path == "/users":
            self.handleUserCreate()
        elif self.path == "/sessions":
            self.handleSessionCreate()
        else:
            self.handleNotFound()

    def do_DELETE(self):
        self.load_session()
        path_parts = self.path.split("/")
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None
        if resource == "songs" and identifier != None:
            self.handleSongDeleteMember(identifier)
        else:
            self.handleNotFound()

    def do_PUT(self):
        self.load_session()
        path_parts = self.path.split("/")
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None
        if  resource == "songs" and identifier == None:
            self.handleNotFound()    
        elif resource == "songs" and identifier != None:
            self.handleSongUpdateMember(identifier)
        else:
            self.handleNotFound()
            
    

def run():
    db = SongDB()
    db.createSongsTable()
    db.createUsersTable()
    db = None # disconnect

    # listen = ("127.0.0.1", 8080)

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)

    print("server listening on", "{}:{}".format(*listen))
    server.serve_forever()


run()



# add this into the code once it's up to date











        # if self.path == "/songs":
        #     self.send_response(200) #<- status code
        #     #headers go here
        #     self.send_header("Access-Control-Allow-Origin", "*")
        #     self.send_header("Content-Type", "application/json")

        #     self.end_headers()

        #     #body goes here
        #     # self.wfile.write(bytes(json.dumps(songs), "utf-8"))
        #     self.wfile.write(bytes(json.dumps(db.getAllSongs()), "utf-8"))
        #     print(db.getAllSongs, "example")


        #     return
        # # elif self.path == "/tigers":

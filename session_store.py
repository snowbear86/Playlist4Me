import os
import base64



class SessionStore:

    def __init__(self):
        self.sessions = {}


    #load the session
    def getSessionData(self, sessionId):
        if sessionId in self.sessions:
            return self.sessions[sessionId]
        #check dictionary for the passed in session id.
        else:
            return None

    #create new session
    def createSession(self):
        sessionId = self.generateSessionId()
        #create a new session with an empty dictionary
        self.sessions[sessionId] = {}
        return sessionId

    def generateSessionId(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

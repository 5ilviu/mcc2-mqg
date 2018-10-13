from user import User, UserFactory
from data_store import Database
from game.gamestate import GameState, Player, Question
import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import random
from threading import Semaphore
__author__ = "silviu"

USERS_FOR_MATCH = 1
QUESTIONS_PER_MATCH = 10
root = os.path.dirname(__file__)

mmsemaphore = Semaphore()
GLOBALS = {
    'sockets': [],
    'games': {},
    'pre_game': []
}


class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "template_path": "templates",
            "static_path": "static",
        }
        handlers = [
            (r"/api/login", LoginHandler),
            (r"/api/user", UserHandler),
            (r"/api/stats", StatisticsHandler),
            (r"/api/game_socket/(.*)", GameSocketHandler),
            (r"/api/pre_game_socket", PreGameSocketHandler),
            (r"/api/mock", PreGameSocketHandlerMock),
            (r"/()", tornado.web.StaticFileHandler, {"path": root + "/static", "default_filename": "index.html"}),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings.get("static_path")}),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)
        self.cookie_secret = "73f956c4ad78d177793c63c5be30ba21"


class PreGameSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        user = getUser(self)
        GLOBALS["pre_game"].append((user, self))
        makeMatch()
        print("PWebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("PWebSocket closed")


class PreGameSocketHandlerMock(tornado.websocket.WebSocketHandler):
    def open(self):
        self.write_message("asd")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("PWebSocket closed")


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_header("Content-Type", "text/javascript")
        try:
            username = self.get_arguments("name")[0]
        except:
            self.set_status(400)
            return
        user = data_store.users.find_one({"username":username})
        if user is None:
            user = User(username)
            data_store.users.insert(user.encode())
        self.set_cookie("username", username)
        self.set_status(200)


class UserHandler(tornado.web.RequestHandler):
    def get(self):
        user = getUser(self)
        if user is not None:
            self.write(user.encode())
        return


class StatisticsHandler(tornado.web.RequestHandler):
    def get(self):
        top = UserFactory.top(data_store)
        res = []
        for u in top:
            res.append(u.encode())
        self.write(json.dumps(res))


class GameSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, gameId):
        user = getUser(self)
        self.gameId = gameId
        print("WebSocket opened {}".format(gameId))
        if gameId in GLOBALS["games"]:
            (gamestate, sessions) = GLOBALS["games"][self.gameId]
            sessions.append(self)
            GLOBALS["games"][self.gameId] = (gamestate, sessions)
            gamestate.user_connected(user)
            broadcast(sessions, gamestate)
        else:
            self.close(404,"Not found")

    def on_message(self, message):
        (gamestate, sessions) = GLOBALS["games"][self.gameId]
        gamestate.handle_action(getUser(self), message)
        broadcast(sessions, gamestate)

    def on_close(self):
        (gamestate, sessions) = GLOBALS["games"][self.gameId]
        sessions.remove(self)
        print("WebSocket closed")

def broadcast(sessions, gamestate):
    for s in sessions:
        s.write_message(gamestate.encode())

def getUser(handler):
    try:
        username = handler.get_cookie("username")
    except:
        handler.set_status(400)
        return
    if username is None:
        handler.set_status(401)
        return
    user = UserFactory.login(username, data_store)
    if user is None:
        self.set_status(404)
        return
    return user

def makeMatch():
    mmsemaphore.acquire()
    if len(GLOBALS["pre_game"]) >= USERS_FOR_MATCH :
        players = []
        sessions = []
        for i in range(USERS_FOR_MATCH):
            (user, session) = GLOBALS["pre_game"].pop(0)
            players.append(Player(user))
            sessions.append(session)
        gamestate = GameState(players, randomQuestions())
        GLOBALS["games"][gamestate.room] = (gamestate, [])
        for sess in sessions:
            sess.write_message(gamestate.room)
    mmsemaphore.release()

def randomQuestions():
    res = []
    dbqs = data_store.questions.aggregate([{"$sample": {"size": QUESTIONS_PER_MATCH}}])
    for dbq in dbqs:
        res.append(Question.decode(dbq))
    return res


if __name__ == "__main__":
    data_store = Database()

    application = Application()
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()


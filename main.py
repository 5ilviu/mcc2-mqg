from user import User, UserFactory
from data_store import Database
from game.gamestate import GameState, Player
import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import random
from threading import Semaphore
__author__ = "silviu"

root = os.path.dirname(__file__)

mmsemaphore = Semaphore()
GLOBALS = {
    'sockets': [],
    'games': [],
    'pre_lobby': []
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
            (r"/api/game_socket", GameSocketHandler),
            (r"/api/pre_game_socket", PreGameSocketHandler),
            (r"/()", tornado.web.StaticFileHandler, {"path": root + "/static", "default_filename": "index.html"}),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings.get("static_path")}),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)
        self.cookie_secret = "73f956c4ad78d177793c63c5be30ba21"


class PreGameSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, name):
        user = getUser(self)
        GLOBALS["pre_lobby"].append(
            {
                "user": user,
                "socket":self
            }
        )
        makeMatch()
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

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
    def open(self, name):
        getUser(self)
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

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
    if len(GLOBALS["pre_game"]) > 2:
        players = []
        sessions = []
        for i in range(3):
            (user, session) = GLOBALS["pre_game"].pop(0)
            players.append(Player(user))
            sessions.append(session)
        gamestate = GameState(players)
        GLOBALS["games"].append(gamestate)
        for sess in sessions:
            sess.write_message(gamestate.room)
    mmsemaphore.release()


if __name__ == "__main__":
    data_store = Database()

    application = Application()
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()


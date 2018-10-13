from user import User, UserFactory
from data_store import Database
import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
__author__ = "silviu"

root = os.path.dirname(__file__)

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
            (r"/api/game_socket/(.*)", GameSocketHandler),
            (r"/()", tornado.web.StaticFileHandler, {"path": root + "/static", "default_filename": "index.html"}),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings.get("static_path")}),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)
        self.cookie_secret = "73f956c4ad78d177793c63c5be30ba21"


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
        self.set_status(200)

class UserHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            username = self.get_arguments("name")[0]
        except:
            self.set_status(400)
            return
        user = UserFactory.login(username,data_store)
        if user is None:
            self.set_status(404)
            return
        self.write(user.encode())
        return


class GameSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, name):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")


if __name__ == "__main__":
    data_store = Database()

    application = Application()
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()


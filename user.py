class User:
    def __init__(self, username, games=None, mmr=0):
        self.username = username
        self.games = games
        self.mmr = mmr

    def encode(self):
        return {"username": self.username,
                "games": self.games,
                "mmr": self.mmr
                }


class UserFactory:
    def __init__(self):
        pass

    @staticmethod
    def decode(obj):
        return User(obj["username"],
                    obj["games"],
                    obj["mmr"])

    @staticmethod
    def login(username, datastore):
        user_list = datastore.users.find_one({"username": username})
        dbuser = UserFactory.decode(user_list)
        return dbuser
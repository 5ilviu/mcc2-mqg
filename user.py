from bson import SON


class User:
    def __init__(self, _id, username, wins=0, lose=0, mmr=0):
        self._id = _id
        self.username = username
        self.wins = wins
        self.mmr = mmr
        self.lose = lose

    def encode(self):
        return {"username": self.username,
                "wins": self.wins,
                "lose": self.lose,
                "mmr": self.mmr
                }


class UserFactory:
    def __init__(self):
        pass

    @staticmethod
    def decode(obj):
        return User(obj["_id"],
                    obj["username"],
                    obj["wins"],
                    obj["lose"],
                    obj["mmr"])

    @staticmethod
    def login(username, datastore):
        user_list = datastore.users.find_one({"username": username})
        dbuser = UserFactory.decode(user_list)
        return dbuser

    @staticmethod
    def top(datastore):
        top = datastore.users.aggregate([{"$sort": SON([("mmr", -1)])}, {"$limit": 10}])
        res = []
        for u in top:
            res.append(UserFactory.decode(u))
        return res

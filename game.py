class Game:
    def __init__(self, _id, users=None, score=None):
        self._id = _id
        if users is None:
            users = []
        self.users = users
        if score is None:
            score = {}
        self.score = score

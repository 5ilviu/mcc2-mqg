import uuid


class GameState:
    def __init__(self, players):
        self.room = uuid.uuid4()
        self.players = players
        self.score = []
        for player in self.players:
            self.score.append(Score(player.user.name))
        self.questions = None
        self.ready = False
        self.isDone = False
        self.questionNr = -1
        pass


class Player:
    def __init__(self, user):
        self.user = user
        self.abilities = None
        self.heroClass = None
        self.ready = False
        self.connected = False


class Score:
    def __init__(self, user, score=0, hp=30, lives=2):
        self.user = user
        self.score = score
        self.hp = hp
        self.lives = lives


class Question:
    def __init__(self, text, typeq, answers, correct):
        self.text = text
        self.typeq = typeq
        self.answers = answers
        self.correct = correct

    def check(self, answer):
        return self.correct is answer

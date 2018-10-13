import uuid

from user import UserFactory


class GameState:
    def __init__(self, players, questions):
        self.players = players
        self.questions = questions
        self.room = str(uuid.uuid4())
        self.score = []
        for player in self.players:
            self.score.append(Score(player.user.username))
        self.ready = False
        self.isDone = False
        self.questionNr = -1

    def user_connected(self, user):
        for player in self.players:
            if player.user.username == user.username:
                player.connected = True

    def handle_action(self, user, message):
        if "READY" in message:
            self.ready = True
            for player in self.players:
                if player.user.username == user.username:
                    player.ready = True
                if not player.ready:
                    self.ready = False
        elif " " is "asd":
            pass

    def encode(self):
        enc_questions = []
        for q in self.questions:
            enc_questions.append(q.encode())
        enc_players = []
        for p in self.players:
            enc_players.append(p.encode())
        enc_score = []
        for s in self.score:
            enc_score.append(s.encode())
        res = {
            "room": self.room,
            "players": enc_players,
            "score": enc_score,
            "questions": enc_questions,
            "ready": self.ready,
            "isDone": self.isDone,
            "questionNr": self.questionNr
        }
        return res


class Player:
    def __init__(self, user, abilities=None, hero_class=None, ready=False, connected=False):
        self.user = user
        self.abilities = abilities
        self.hero_class = hero_class
        self.ready = ready
        self.connected = connected

    @staticmethod
    def decode(obj):
        return Player(
            UserFactory.decode(obj["user"]),
            obj["abilities"],
            obj["hero_class"],
            obj["ready"],
            obj["connected"]
        )

    def encode(self):
        res = {
            "user": self.user.encode(),
            "abilities": self.abilities,
            "hero_class": self.hero_class,
            "ready": self.ready,
            "connected": self.ready
        }
        return res


class Score:
    def __init__(self, user, score=0, hp=30, lives=2):
        self.user = user
        self.score = score
        self.hp = hp
        self.lives = lives

    @staticmethod
    def decode(obj):
        return Score(
            UserFactory.decode(obj["user"]),
            obj["score"],
            obj["hp"],
            obj["lives"],
        )

    def encode(self):
        res = {
            "user": self.user.encode(),
            "score": self.score,
            "hp": self.hp,
            "lives": self.lives
        }
        return res


class Question:
    def __init__(self, text, typeq, answers, correct):
        self.text = text
        # 0 quiz, 1 closest nr
        self.typeq = typeq
        self.answers = answers
        self.correct = correct

    @staticmethod
    def decode(dbo):
        return Question(dbo["text"], dbo["typeq"], dbo["answers"], dbo["correct"])

    def check(self, answer):
        return self.correct is answer

    def encode(self):
        res = {
            "text": self.text,
            "typeq": self.typeq,
            "answers": self.answers,
            "correct": self.correct
        }
        return res

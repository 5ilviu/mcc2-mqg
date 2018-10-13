import uuid

import time

from user import UserFactory

QUESTION_TIME = 10
QUESTION_NUMBER = 3


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
        self.questions_start = 0

    def user_connected(self, user):
        for player in self.players:
            if player.user.username == user.username:
                player.connected = True

    def check_time(self):
        if (time.time() - self.questions_start) > QUESTION_TIME:
            self.new_question()
            return True
        return False

    def handle_action(self, user, message):
        if "READY" in message:
            for player in self.players:
                if player.user.username == user.username:
                    player.ready = True
            self.ready = True
            for player in self.players:
                if not player.ready:
                    self.ready = False
            if self.ready:
                self.questionNr = 0
                self.questions_start = time.time()
        elif "ANSWER" in message:
            if (time.time() - self.questions_start) > QUESTION_TIME:
                self.new_question()
            if self.isDone:
                return
            for player in self.players:
                if player.user.username == user.username:
                    if player.blocked:
                        return
                    else:
                        player.blocked = True
            ans = str(message).replace("ANSWER ", "")
            print ans
            if self.questions[self.questionNr].correct == ans:
                for rec in self.score:
                    if rec.user == user.username:
                        rec.score += 10 - (time.time() - self.questions_start) * 9
            else:
                for rec in self.score:
                    if rec.user == user.username:
                        rec.hp -= 10
                        if rec.hp < 0:
                            rec.lives -= 1
                            if rec.lives == 0:
                                for player in self.players:
                                    if player.user.username == user.username:
                                        player.blocked = True

        elif "ABILITY" in message:
            ability = str(message).replace("ABILITY ", "")
            print ability
            pass

    def new_question(self):
        for player in self.players:
            for s in self.score:
                if player.user.username == s.user:
                    if s.lives != 0:
                        player.blocked = False
        self.questionNr += 1
        self.questions_start = time.time()
        self.check_endgame()

    def check_endgame(self):
        if QUESTION_NUMBER <= self.questionNr:
            self.isDone = True
            for player in self.players:
                for sc in self.score:
                    if sc.user == player.user.username:
                        player.user.mmr += sc.score

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
            "questionNr": self.questionNr,
            "questions_start": self.questions_start
        }
        return res


class Player:
    def __init__(self, user, abilities=None, hero_class=None, ready=False, connected=False, blocked=False):
        self.user = user
        self.abilities = abilities
        self.hero_class = hero_class
        self.ready = ready
        self.connected = connected
        self.blocked = blocked

    @staticmethod
    def decode(obj):
        return Player(
            UserFactory.decode(obj["user"]),
            obj["abilities"],
            obj["hero_class"],
            obj["ready"],
            obj["connected"],
            obj["blocked"]
        )

    def encode(self):
        res = {
            "user": self.user.encode(),
            "abilities": self.abilities,
            "hero_class": self.hero_class,
            "ready": self.ready,
            "connected": self.connected,
            "blocked": self.blocked
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

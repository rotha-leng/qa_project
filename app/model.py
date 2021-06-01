import datetime
from app import app, db, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user


class MKT_USER(UserMixin, db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(50))
    Email_Address = db.Column(db.String(75))
    Password = db.Column(db.String(200))
    Avatar = db.Column(db.String(100))
    Created = db.Column(db.String(50), default=datetime.datetime.utcnow)

    def get_id(self):
        return self.ID


    def __init__(self, FullName, Email_Address, Password, Avatar, Created):
        self.FullName = FullName
        self.Email_Address = Email_Address
        self.Password = Password
        self.Avatar = Avatar
        self.Created = Created

@login_manager.user_loader
def load_user(user_id):
   return MKT_USER.query.get(int(user_id))



class MKT_QUESTION(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Question_Tittle = db.Column(db.String(75))
    Question_body = db.Column(db.Text)
    Tag_Topic = db.Column(db.String(150))
    Vote = db.Column(db.Integer)
    User = db.Column(db.Integer, default='')
    Best_Answer = db.Column((db.Integer))
    Created = db.Column(db.String(20), default=datetime.datetime.utcnow)


    def __init__(self, Question_Tittle, Question_body, Tag_Topic, Vote, User, Best_Answer, Created):
        self.Question_Tittle = Question_Tittle
        self.Question_body = Question_body
        self.Tag_Topic = Tag_Topic
        self.Vote = Vote
        self.User = User
        self.Best_Answer = Best_Answer
        self.Created = Created

class  MKT_ANSWER(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    QuestionID = db.Column(db.Integer)
    Answer = db.Column(db.Text)
    User = db.Column(db.Integer)
    Created_On = db.Column(db.String(10))

    def __init__(self, QuestionID, Answer, User, Created_On):
        self.QuestionID = QuestionID
        self.Answer = Answer
        self.User = User
        self.Created_On = Created_On

class  MKT_VOTE(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Question_ID = db.Column(db.Integer)
    User_ID = db.Column(db.Integer)
    Created_On = db.Column(db.String(10))

    def __init__(self, Question_ID, User_ID, Created_On):
        self.Question_ID = Question_ID
        self.User_ID = User_ID
        self.Created_On = Created_On


class MKT_COMMENT(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Question_ID = db.Column(db.Integer)
    Comment = db.Column(db.Text)
    User_ID = db.Column(db.Integer)
    Created_On = db.Column(db.String(10))


    def __init__(self, Question_ID, Comment, User_ID, Created_On):
        self.Question_ID = Question_ID
        self.Comment = Comment
        self.User_ID = User_ID
        self.Created_On = Created_On

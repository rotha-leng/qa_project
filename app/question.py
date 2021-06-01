from .model import *
from app import db, app
import sqlalchemy
from sqlalchemy.sql.expression import cast

import datetime

from flask import render_template, request, url_for, flash, redirect, jsonify, json

from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField
from wtforms import validators, ValidationError
from sqlalchemy import or_
from hashlib import md5
from flask_avatars import Avatars

avatars = Avatars(app)


class searchQA(Form):
	searchbox = TextField("Search", [validators.Required("Please Enter your Title!")])


@app.route('/', methods=['POST', 'GET'])
def getPost():
	search = request.args.get('Search')
	if search == None:
		totalQA = MKT_QUESTION.query.count()
		question = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic,MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User). \
		order_by(MKT_QUESTION.Created.desc()).limit(5).all()

	else:
		search = "%{}%".format(search)
		question = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic,MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User). \
			filter(or_
				(MKT_QUESTION.Question_Tittle.like("%"f"{search}""%"),
				MKT_QUESTION.Question_body.like("%"f"{search}""%"),
		        MKT_QUESTION.Tag_Topic.like("%"f"{search}""%")))
		totalQA = question.count()


	return render_template('home/index.html', posts=question, totalQA=totalQA)


@app.route('/Reload')
def reload():
	totalQA = MKT_QUESTION.query.count()
	question = db.session. \
		query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic,
			  MKT_QUESTION.Created, MKT_USER.FullName). \
		join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User). \
		order_by(MKT_QUESTION.Created.desc()).all()
	return render_template('home/index.html', posts=question, totalQA=totalQA)

@app.route('/All')
def all():
	totalQA = MKT_QUESTION.query.count()
	question = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic, MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User). \
		all()
	return render_template('home/index.html', posts=question, totalQA=totalQA)

@app.route('/MostRecent')
def mostrecent():
	totalQA = MKT_QUESTION.query.count()
	question = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic,MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User). \
		order_by(MKT_QUESTION.Created.desc()).limit(5).\
		all()
	return render_template('home/index.html', posts=question, totalQA=totalQA)



class PostForm(Form):
	username = TextField(" Full Name :", [validators.Required("Enter a name"), validators.Length(min=5, max=20, message="Full Name Cannot less than 5 or more then 20")])
	EmailAddress = TextField(" Email Address :", [validators.Required("Enter your email address")])
	password = PasswordField(" Password :", [validators.Required("Create a password"), validators.Length(min=6,  message="Password Cannot less then 6")])


	def validate_EmailAddress(form, field):
		title = field.data
		postObj = MKT_USER.query.filter_by(Email_Address=title)
		if postObj.first():
			raise ValidationError(f'Post title {title} already exist!')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = PostForm()
	if request.method == 'POST':

		if form.validate() == True:

			fullname = request.form['username']
			emailaddress = request.form['EmailAddress']
			password = request.form['password']
			passwords = generate_password_hash(password)
			Avatar = 'https://www.gravatar.com/avatar/' + md5(b'Email').hexdigest()
			register = MKT_USER(FullName=fullname, Email_Address=emailaddress, Password=passwords, Avatar=Avatar, Created=datetime.datetime.now())
			db.session.add(register)
			db.session.commit()
			flash("Your Sign up have been successfully, Please click Sign in at bottom!")
			return redirect(url_for('register'))

	return render_template("auth/register.html", form=form)



@app.route('/Login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		emailaddress = request.form['email']
		password = request.form['password']

		authObj = MKT_USER.query.filter_by(Email_Address=emailaddress).first()
		if check_password_hash(authObj.Password, password) == True:
			login_user(authObj)
			return redirect(url_for('getPost'))
		else:
			flash("Incorrect Email Address or Password!")

	return render_template('auth/login.html')


class AskForm(Form):
	Title = TextField("Question Title", [validators.Required("Please enter post title."), validators.Length(min=10, max=100,message="Post Title Cannot less than 10 or more then 100")])
	Body = TextAreaField("Question Body", [validators.Required("Please enter post content.")])
	Tag = TextField("Tag and Topic", [validators.Required("Select Tags for the Question")])

	def validate_Title(form, field):
		title = field.data
		postObj = MKT_QUESTION.query.filter_by(Question_Tittle=title)

		if postObj.first():
			raise ValidationError(f'Post title {title} already exist!')


@app.route('/ask', methods=['GET', 'POST'])
@login_required
def askQuestion():
	form = AskForm()
	if request.method == 'POST':

		if form.validate() == True:
			Title = request.form['Title']
			Body = request.form['Body']
			Tag = request.form['Tag']
			AuthorID = current_user.get_id()

			Posts = MKT_QUESTION(Question_Tittle=Title, Question_body=Body, Tag_Topic=Tag, Vote=0, Best_Answer=0, User=AuthorID, Created=datetime.datetime.now().strftime("%x-%X"))

			db.session.add(Posts)
			db.session.commit()
			flash('Your Post has been added successfully.')
			return redirect(url_for('getPost'))
	return render_template('question/create.html', form=form)


@app.route('/Logout')
@login_required
def logout():
	logout_user()
	flash('You are now logout! Please Sign in again.')
	return redirect(url_for('index'))




class CommentForm(Form):
	Comment = TextField("Leave a comment", [validators.Required("Please enter post content.")])
	Answer = TextAreaField("Submit an answer", [validators.Required("Please enter post content.")])
	btncomment = SubmitField("Comment")
	btnanswer = SubmitField("Answer")
	vote = SubmitField("vote")

"""def getRelatedPost(search):
	# search = request.args.get('Search')
	# postList = []
	print('search:', search)
	if search:
		postObj = MKT_QUESTION.query.limit(5).all()
		print(postObj)
		# .filter(MKT_QUESTION.Question_Tittle.contains(search))\

		return postObj
	return ''
	"""


@app.route('/View/Question/<int:QuestionID>')
@app.route('/View/Question/')
def ViewQuestionAnswer(QuestionID=''):
	form = CommentForm()

	if QuestionID == '':


		totalV = MKT_VOTE.query.count()
		Question = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic, MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User).all()

		limit = MKT_QUESTION.query.order_by(MKT_QUESTION.Created.desc()).limit(5).all()

		Answer = MKT_ANSWER.query.all()
		totalA = len(Answer)

		Comment = MKT_COMMENT.query.all()
		totalcmt = len(Comment)

		ID = current_user.get_id()
		user = MKT_USER.query.get(ID)

		Vote = db.session.query(MKT_VOTE.ID).filter(MKT_VOTE.Question_ID == QuestionID).all()

		Avatar = 'https://www.gravatar.com/avatar/' + md5(b'Email').hexdigest()

	else:

		Question = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Question_Tittle, MKT_QUESTION.Question_body, MKT_QUESTION.Tag_Topic, MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID == MKT_QUESTION.User).filter(MKT_QUESTION.ID == QuestionID)

		limit = MKT_QUESTION.query.order_by(MKT_QUESTION.Created.desc()).limit(5).all()

		Answer = db.session.query(MKT_ANSWER.Answer, MKT_USER.FullName, MKT_ANSWER.Created_On).join(MKT_USER, MKT_USER.ID == MKT_ANSWER.User).filter(MKT_ANSWER.QuestionID == QuestionID).all()
		totalA = len(Answer)

		Comment = db.session.query(MKT_COMMENT.Comment, MKT_USER.FullName, MKT_COMMENT.Created_On).join(MKT_USER, MKT_USER.ID == MKT_COMMENT.User_ID).\
			filter(MKT_COMMENT.Question_ID == QuestionID).all()
		totalcmt = len(Comment)

		ID = current_user.get_id()
		user = MKT_USER.query.get(ID)

		Vote = db.session.query(MKT_VOTE.ID).join(MKT_USER, MKT_USER.ID == MKT_VOTE.User_ID).filter(MKT_VOTE.Question_ID == QuestionID).all()
		totalV = len(Vote)

		Avatar = 'https://www.gravatar.com/avatar/' + md5(b'Email').hexdigest()

		if Question.first() is None:
			abort(404)

	return render_template('question/index.html', Question=Question, form=form, Answer=Answer, Comment=Comment, vote=totalV, Vote=Vote, TotalA=totalA, User=user, Totalcmt=totalcmt, Limit=limit, Avatar=Avatar)




@app.route('/Answer/Question/<int:QuestionID>', methods=["POST"])
def AnswerQuestion(QuestionID):
	form = CommentForm()
	if request.method == 'POST':

		if form.validate() == False:
			AnswerGet = request.form['Answer']
			AuthorID = current_user.get_id()
			Question = MKT_ANSWER(QuestionID=QuestionID, Answer=AnswerGet, User=AuthorID, Created_On=datetime.datetime.now().strftime("%d-%m-%Y"))
			db.session.add(Question)
			db.session.commit()

			return redirect(url_for('index'))

	return render_template('question/index.html', form=form)


@app.route('/Comment/Question/<int:QuestionID>', methods=["GET", "POST"])
def CommentQuestion(QuestionID):
	form = CommentForm()

	if request.method == 'POST':

		if form.validate() == False:
			CommentGet = request.form['Comment']
			AuthorID = current_user.get_id()
			Comment = MKT_COMMENT(Question_ID=QuestionID, Comment=CommentGet, User_ID=AuthorID, Created_On=datetime.datetime.now().strftime("%d-%m-%Y"))

			db.session.add(Comment)
			db.session.commit()

			return redirect(url_for('index'))

	return render_template('question/index.html', form=form)


@app.route('/ManagePost')
@login_required
def managePost():
	ID = current_user.get_id()

	authorObj = MKT_USER.query.get(ID)
	postByAuthObj = MKT_QUESTION.query.filter_by(User=str(ID)).all()
	Avatar = 'https://www.gravatar.com/avatar/' + md5(b'Email').hexdigest()
	if postByAuthObj:
		return render_template('question/update.html', Question=postByAuthObj, user=authorObj, Avatar=Avatar)
	else:
		return render_template('question/update.html')

@app.route('/View/Question/<int:QuestionID>/Delete')
@login_required
def deletePost(QuestionID):
	if QuestionID:
		MKT_QUESTION.query.filter_by(ID=QuestionID).delete()
		db.session.commit()
		flash(f'Your post has been deleted successfully')
	return redirect(url_for('managePost'))


@app.route('/View/Question/<int:QuestionID>/Edit', methods=['GET', 'POST'])
@login_required
def editPost(QuestionID=''):
	form = AskForm()

	if request.method == 'POST':
		PostObj = MKT_QUESTION.query. \
			filter_by(ID=QuestionID). \
			first()  # .update({'Content':request.form['Content']})

		PostObj.Question_Title = request.form['Title']
		PostObj.Question_body = request.form['Content']
		PostObj.Tag_Topic = request.form['Tag']
		db.session.commit()
		flash("Update post Successfully!")

	if QuestionID:
		postobj = MKT_QUESTION.query.get(QuestionID)

		if postobj:
			form.Title.data = postobj.Question_Tittle
			form.Body.data = postobj.Question_body
			form.Tag.data = postobj.Tag_Topic
			return render_template('question/create.html', form=form)
	abort(404)



@app.route('/Upvote/Question/<int:QuestionID>', methods=["GET", "POST"])
def upvote1(QuestionID):
	form = CommentForm()

	if request.method == 'POST':

		if form.validate() == False:
			AuthorID = current_user.get_id()
			vote = MKT_VOTE(Question_ID=QuestionID, User_ID=AuthorID, Created_On=datetime.datetime.now().strftime("%Y-%m-%d"))
			db.session.add(vote)
			db.session.commit()

			return redirect(url_for('index'))

	return render_template('question/index.html', form=form)




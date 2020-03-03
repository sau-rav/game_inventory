import os, math, time
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import db, functions

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin): 
	id = None
	password = None

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])

@login_manager.user_loader
def load_user(id):
    if db.exists(id):
        user = User()
        user.id = id
        user.password = db.get_pass(id)
        return user
    return None

@app.route('/')
def index():
	per_page = 10
	page = request.args.get('page', 1, type=int)
	query = request.args.get('query', '', type=str)
	query_type = request.args.get('query_type', 0, type=int)
	own_id = request.args.get('own', -1, type=int)
	if own_id > 0 and current_user.get_id() != None:
		if db.inGamesAndNotOwned(current_user.id,own_id):
			db.ownGame(current_user.id, own_id)
	if query == '':
		game_data = db.get_game_data('', 0)
	else:
		game_data = db.get_game_data(query, query_type)
	game_list = game_data[0][10*(page-1):(10*(page-1)+per_page)]
	list_size = math.ceil(game_data[1]/per_page)
	if list_size == 0:
		list_size = 1
	disp_list = functions.disp_list_generator(page, list_size)
	if page != list_size:
		for i in range(per_page):
			cat_list = functions.extract_data(game_list[i][4], ';')
			game_list[i] += (cat_list,)
			if current_user.get_id() != None:
				flag = db.doesUserOwn(current_user.id, game_list[i][0])
				if flag:
					game_list[i] += (True,)
				else:
					game_list[i] += (False,)
	else:
		for i in range(game_data[1]%per_page):
			cat_list = functions.extract_data(game_list[i][4], ';')
			game_list[i] += (cat_list,)
			if current_user.get_id() != None:
				flag = db.doesUserOwn(current_user.id, game_list[i][0])
				if flag:
					game_list[i] += (True,)
				else:
					game_list[i] += (False,)
	if query == '':
		if current_user.get_id() != None:
			return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, name=current_user.id)
		else:
			return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page)
	else:
		if query_type == 1:
			if current_user.get_id() != None:
				return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, filter = query, query_type = 1, name=current_user.id)
			else:
				return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, filter = query, query_type = 1)
		elif query_type == 2:
			if current_user.get_id() != None:
				return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, filter = query, query_type = 2, name=current_user.id)
			else:
				return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, filter = query, query_type = 2)
		elif query_type == 3:
			if current_user.get_id() != None:
				return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, filter = query, query_type = 3, name=current_user.id)
			else:
				return render_template('index.html', game_list = game_list, disp_list = disp_list, page = page, filter = query, query_type = 3)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if db.exists(form.username.data):
            pswd = db.get_pass(form.username.data)
            if form.password.data == pswd:
                user = User()
                user.id = form.username.data
                user.password = pswd
                login_user(user)
                return redirect(url_for('dashboard'))
            return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        if not db.exists(form.username.data):
            db.insert_into_users_db(form.username.data, form.password.data)
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
	per_page = 10
	page = request.args.get('page', 1, type=int)
	game_data = db.user_owned_games(current_user.id)
	game_list = game_data[0][10*(page-1):(10*(page-1)+per_page)] 
	list_size = math.ceil(game_data[1]/per_page)
	if list_size == 0:
		list_size = 1
	disp_list = functions.disp_list_generator(page, list_size)
	recommended_games = db.recommendGames(current_user.id)
	if page != list_size:
	    for i in range(per_page):
	        cat_list = functions.extract_data(game_list[i][4], ';')
	        game_list[i] += (cat_list,)
	else:
	    for i in range(game_data[1]%per_page):
	        cat_list = functions.extract_data(game_list[i][4], ';')
	        game_list[i] += (cat_list,) 
	return render_template('dashboard.html', game_list = game_list, disp_list = disp_list, page = page, name=current_user.id, recommended_games = recommended_games)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/<id>')
def game_page(id):
	own_id = request.args.get('own', -1, type=int)
	vote = request.args.get('vote', -1, type=int)
	if vote != -1 and current_user.get_id() != None:
		db.changeVote(current_user.id, id, vote)
	if own_id > 0 and current_user.get_id() != None:
		if db.inGamesAndNotOwned(current_user.id,own_id):
			db.ownGame(current_user.id, own_id)
	data = db.get_full_data(id)
	date_converted = data[2].strftime("%d-%b-%Y")
	data += (date_converted,)
	platform_converted = functions.extract_data(data[6], ';')
	data += (platform_converted,)
	if current_user.get_id() != None:
		flag = db.doesUserOwn(current_user.id, data[0])
		if flag:
			data += (True,)
			vote_status = db.getVote(current_user.id, data[0])
			if vote_status == 0:
				data += (0,)
			elif vote_status == 1:
				data += (1,)
			else:
				data += (2,)
		else:
			data += (False,)
	similar_games_data = db.getSimilarGames(data[10], data[0])
	if current_user.get_id() != None:
		return render_template('game.html', game_data = data, name=current_user.id, similar_games_data = similar_games_data)
	else:
		return render_template('game.html', game_data = data, similar_games_data = similar_games_data)

@app.route('/about')
def about():
	if current_user.get_id() != None:
		return render_template('about.html', name=current_user.id)
	else:
		return render_template('about.html')

if __name__ == '__main__':
	app.run(host = os.getenv('IP', 'localhost'), port = int(os.getenv('PORT', 8000)), debug = True)
	#app.run(host= 'localhost', port=5432, debug=True)
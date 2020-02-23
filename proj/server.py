import os
from flask import Flask, render_template, request
import db
app = Flask(__name__)


@app.route('/')
def root_html():
	return render_template('games.html', game_list = db.get_sample())

if __name__ == '__main__':
	app.run(host = os.getenv('IP', 'localhost'), port = int(os.getenv('PORT', 8000)), debug = True)
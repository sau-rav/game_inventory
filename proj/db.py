import psycopg2

def connectToDb():
	try:
		return psycopg2.connect("host=localhost dbname=dbms user=saurav password=saurav")
	except:
		e = sys.exc_info()[0]
		write_to_page("<p>Error: %s</p>")

def get_game_data(filter):
	conn = connectToDb()
	cur = conn.cursor()
	if filter == '':
		cur.execute("select * from home_page_data")
		sample_data = cur.fetchall()
		sample_data = [sample_data, len(sample_data)]
	else:
		cur.execute("select * from home_page_data")
		sample_data = cur.fetchall()
		sample_data = [sample_data, len(sample_data)]
	cur.close()
	conn.close()
	return sample_data

def get_full_data(id):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("select * from home_page_data")
	data = cur.fetchall()
	cur.close()
	conn.close()
	return data

def exists(username):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("select * from users where username = %(username)s", {'username': username})
	is_exist = cur.fetchone()
	cur.close()
	conn.close()
	return is_exist is not None

def get_pass(username):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("select passwords from users where username = %(username)s", {'username': username})
	password = cur.fetchone()
	cur.close()
	conn.close()
	return password[0]

def insert_into_users_db(username, password):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("insert into users(username, passwords) values (%s, %s)", (username, password))
	conn.commit()
	cur.close()
	conn.close()
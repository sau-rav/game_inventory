import psycopg2

def connectToDb():
	try:
		return psycopg2.connect("host=localhost dbname=<dbname> user=<username> password=<password>")
	except:
		e = sys.exc_info()[0]
		write_to_page("<p>Error: %s</p>")

def get_game_data(filter, query_type):
	conn = connectToDb()
	cur = conn.cursor()
	if filter == '':
		cur.execute("select * from home_page_data")
		sample_data = cur.fetchall()
		sample_data = [sample_data, len(sample_data)]
	else:
		if query_type == 1:
			# on basis of steamspy_tags
			cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam where string_to_array((%s), ';') <@ string_to_array(steamspy_tags, ';')", (filter,))
			sample_data = cur.fetchall()
			sample_data = [sample_data, len(sample_data)]
		elif query_type == 2:
			# on basis of game name
			cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam where LOWER(name) like LOWER('%{}%')".format(filter))
			sample_data = cur.fetchall()
			sample_data = [sample_data, len(sample_data)]
		elif query_type == 3:
			# for the right menu
			# filter = rating desc
			# filter = date newest first
			# filter = sell desc
			# filter = playtime asc
			# filter = price asc
			if filter == 'rating':
				cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam order by positive_ratings desc")
			elif filter == 'date':
				cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam order by release_date desc")
			elif filter == 'sell':
				cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam order by (string_to_array(owners, '-'))[0]::int + (string_to_array(owners, '-'))[1]::int desc")
			elif filter == 'playtime':
				cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam order by average_playtime asc")
			elif filter == 'price':
				cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam order by price asc")
			sample_data = cur.fetchall()
			sample_data = [sample_data, len(sample_data)]
		# return sample data in form of [sampledata, len(sampledata)]
		# columns are steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative ratings, price, header_image
	cur.close()
	conn.close()
	return sample_data

def get_full_data(id):
	conn = connectToDb()
	cur = conn.cursor()
	query ='''
		select * from steam s
		left join description d on d.steam_appid = s.appid
		left join media m on m.steam_appid = s.appid
		left join requirements r on r.steam_appid = s.appid
		where s.appid = {0};
	'''
	cur.execute(query.format(id))
	data = cur.fetchall()[0]
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

def user_owned_games(username):
	conn = connectToDb()
	cur = conn.cursor()
	query ='''
	select * from home_page_data
	where steam_appid in (select gameid from users_games where username='{0}');
	'''
	cur.execute(query.format(username))

	data = cur.fetchall()
	cur.close()
	conn.close()
	return data,len(data)

def doesUserOwn(username, gameid):
	conn = connectToDb()
	cur = conn.cursor()
	query = "select * from users_games where username='{}' and gameid={}".format(username, gameid)
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
	conn.close()
	return len(data) > 0

def inGamesAndNotOwned(username, gameid):
	conn = connectToDb()
	cur = conn.cursor()
	query = "select steam_appid from home_page_data where steam_appid not in (select gameid from users_games where username='{}') and steam_appid = {};".format(username, gameid)
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
	conn.close()
	return len(data) > 0

def ownGame(username, gameid):
	conn = connectToDb()
	cur = conn.cursor()
	query = "insert into users_games(username,gameid) values ('{}', {});".format(username, gameid)
	cur.execute(query)
	conn.commit()
	cur.close()
	conn.close()

def getSimilarGames(tags, id):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("select steam_appid, name, header_image from media_join_steam where string_to_array('{}', ';') <@ string_to_array(steamspy_tags, ';') and steam_appid <> {} limit 9".format(tags, id))
	data = cur.fetchall()
	cur.close()
	conn.close()
	return data

def recommendGames(username):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("create view games_played as select gameid from users_games where username = '{}';".format(username))
	cur.execute('create view popular_tag as select tags from games_played join games_tags on games_played.gameid = games_tags.appid group by tags order by count(*) desc limit 1;')
	cur.execute('select steam_appid, name, header_image from games_tags, popular_tag, media_join_steam where popular_tag.tags = games_tags.tags and games_tags.appid = media_join_steam.steam_appid and not exists(select from games_played where games_played.gameid = media_join_steam.steam_appid) order by positive_ratings desc limit 9;')
	data = cur.fetchall()
	if len(data) == 0:
		cur.execute('select steam_appid, name, header_image from media_join_steam order by positive_ratings desc limit 9;')
		data = cur.fetchall()
	cur.close()
	conn.close()
	return data

def changeVote(username, gameid, vote):
	conn = connectToDb()
	cur = conn.cursor()
	if vote == 2:
		#set null
		cur.execute('''update users_games set review = null where username = '{0}' and gameid = {1}'''.format(username, gameid))
	else:
		#set value
		cur.execute('''update users_games set review = {0} where username = '{1}' and gameid = {2}'''.format(vote, username, gameid))
	conn.commit()
	cur.close()
	conn.close()

def getVote(username, gameid):
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("select review from users_games where username = '{0}' and gameid = {1}".format(username, gameid))
	data = cur.fetchall()
	cur.close()
	conn.close()
	if data[0][0] == None:
		return 2
	return data[0][0]


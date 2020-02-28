import psycopg2

def connectToDb():
	try:
		return psycopg2.connect("host=localhost dbname=dbms user=saurav password=saurav")
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
			cur.execute("select steam_appid, name, developer, genres, steamspy_tags, positive_ratings, negative_ratings, price, header_image from media_join_steam where name like '%(%s)%'", (filter,))
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
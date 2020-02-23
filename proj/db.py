import psycopg2

def connectToDb():
	try:
		return psycopg2.connect("host=localhost dbname=dbms user=saurav password=saurav")
	except:
		e = sys.exc_info()[0]
		write_to_page("<p>Error: %s</p>")

def get_sample():
	conn = connectToDb()
	cur = conn.cursor()
	cur.execute("select * from steam limit 5")
	sample_data = cur.fetchall()
	print(sample_data)
	cur.close()
	conn.close()
	return sample_data
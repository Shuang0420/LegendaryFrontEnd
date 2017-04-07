# views.py

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psycopg2
import hashlib
import datetime as DT
import re


def getConnection(): 
	""" Obtain connection to Redshift """
	conn = psycopg2.connect(
	#host='cmucapstone.cvtax4qegotm.us-west-2.redshift.amazonaws.com', # Dummy DB
	host='cmucapstone.cjvi8xu2ejaw.us-east-2.redshift.amazonaws.com', 
	password='Ngl91dY2daIa3wFD1QhL',
	dbname='cmucapstonejd',
	user='cmucapstonejd', 
	port='5439')
	return conn


def format(rows, fields):
	"""
	Format a query result (a list of tuples) to an array of JSON objects
	@rows: a list of sql results in tuples
	@fields: a list of column names
	@return: an array of json objects
	"""
	try:
		result = []
		if rows == None or fields == None:
			raise ValueError('Null input')
		if len(rows) == 0:
			return result
		if len(rows[0]) != len(fields):
			raise ValueError('Inconsistent field lengths')
		result = (dict(zip(fields,row)) for row in rows)
		return result
	except ValueError as err:
		return (err) 


def hashMD5(userID, password):
	""" 
	Create a MD5 hash of a string 
	@userID: userID to be reversed and used as salt
	@password: password entered by user
	@return: the MD5 hash for salted password
	"""
	string = userID[::-1] + password 
	return hashlib.md5(string.encode('utf-8')).hexdigest()


@api_view(['POST'])
def auth(request):
	"""
	Authenticate user login given the userID and password
	"""
	conn = getConnection()
	cur = conn.cursor()
	id = request.data.get('userID')
	pd = request.data.get('password')

	# incomplete input
	if id == None or pd == None:
		conn.close()
		return Response("The userID or password is missing.", status=status.HTTP_400_BAD_REQUEST)
	
	# locate user by userID
	fields = ['userID', 'name', 'password', 'role']
	try:
		sql = "SELECT {} FROM userinfo WHERE userID = \'{}\';".format(",".join(fields), id)
		cur.execute(sql)
		result = cur.fetchall()

		# userID does not exist
		if len(result) == 0:
			return Response("The userID does not exist.", status=status.HTTP_400_BAD_REQUEST)

		# userID exists, check password
		if hashMD5(id, pd) != result[0][2]:
			return Response("Password is incorrect.", status=status.HTTP_400_BAD_REQUEST)
		fields.remove('password')
		result = [(userID, name, role) for userID, name, password, role in result]
		return Response(format(result,fields), status=status.HTTP_200_OK)

	except psycopg2.ProgrammingError as e:
		print (repr(e))
		conn.close()
		return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def user(request):
	conn = getConnection()
	cur = conn.cursor()

	if request.method == 'GET':
		"""
		Get the userID and name for a particular user or all users
		"""
		key = request.path.split("user/")[1].replace("/","")
		fields = ['userID', 'name', 'role']
		try:
			# if no userID specified, return all users
			if len(key) == 0:
				sql = "SELECT {} FROM userinfo ORDER BY userID;".format(",".join(fields))
			else :
				sql = "SELECT {} FROM userinfo WHERE userID = \'{}\' ORDER BY userID;".format(",".join(fields), key)
			cur.execute(sql)
			result = cur.fetchall()
			conn.close()
			if len(result) == 0:
				return Response("Invalid userID.", status=status.HTTP_400_BAD_REQUEST)
			return Response(format(result,fields), status=status.HTTP_200_OK)

		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)

	elif request.method == 'PUT':
		"""
		Change user name or password
		"""
		data = request.data
		id = data.get('userID')
		if id == None:
			conn.close()
			return Response("The userID is missing.", status=status.HTTP_400_BAD_REQUEST)
		try:
			# extract the fields that user wants to change
			updates = []
			for key, value in data.items():
				if key == 'userID':
					continue
				if key == 'password':
					value = hashMD5(id, value)
				updates.append(key + " = '" + value + "'")
			
			# run the query
			sql = "UPDATE userinfo SET {} WHERE userID = \'{}\';".format(",".join(updates), id)
			cur.execute(sql)
			conn.commit()
			conn.close()

			# update unsuccessful
			if cur.rowcount == 0:
				return Response("Invalid userID.", status=status.HTTP_400_BAD_REQUEST)

			return Response("User info has been updated.", status=status.HTTP_200_OK)

		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)

	elif request.method == 'POST':
		"""
		Create a new user
		"""
		id = request.data.get('userID')
		name = request.data.get('name')
		pd = request.data.get('password')
		role = request.data.get('role') or 'user'
		if id == None or name == None or pd == None:
			conn.close()
			return Response("The userID/name/password is missing.", status=status.HTTP_400_BAD_REQUEST)
		try:
			# check if the userID is already in use
			sql = "SELECT userID FROM userinfo WHERE userID = \'{}\';".format(id)
			cur.execute(sql)
			result = cur.fetchall()
			if len(result) != 0:
				conn.close()
				return Response("This userID is already in use.", status=status.HTTP_400_BAD_REQUEST)
			
			# if available, create a new user entry
			pd = hashMD5(id,pd)
			sql = "INSERT INTO userinfo (userID, name, password, role) VALUES (\'{}\', \'{}\', \'{}\', \'{}\')".format(id, name, pd, role)
			cur.execute(sql)
			conn.commit()
			conn.close()
			return Response("The user is added successfully.", status=status.HTTP_200_OK)

		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)	
	
	elif request.method == 'DELETE':
		"""
		Remove a user
		"""
		try:
			key = request.path.split("user/")[1].replace("/","")
			sql = "DELETE FROM userinfo WHERE userID = \'{}\';".format(key)
			cur.execute(sql)
			conn.commit()
			conn.close()
			if cur.rowcount == 0:
				return Response("Empty/Invalid userID.", status=status.HTTP_400_BAD_REQUEST)
			return Response("The user has been removed from database.", status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def favoriteAiring(request):
	"""
	Get the airing info for user's favorite shows within a given period of time.

	"""
	conn = getConnection()
	cur = conn.cursor()
	id = request.data.get('userID')
	timeRange = request.data.get('timeRange')
	statistic = request.data.get('statistic') # listing or hour
	if id == None or timeRange == None or statistic == None or statistic not in ('listing', 'hour'):
		conn.close()
		return Response("The userID/timeRange/statistic is missing. The statistic has to be either 'listing' or 'hour'.", status=status.HTTP_400_BAD_REQUEST)
		
	# set date range
	today = str(DT.date.today())
	date_bound = DT.date.today() + DT.timedelta(days=timeRange)
	if today > date_bound:
		date_clause = "airDateTime BETWEEN '" + date_bound + "' AND dateadd(day,1,'" + today + "')"
	else:
		date_clause = "airDateTime BETWEEN '" + today + "' AND dateadd(day,1,'" + date_bound + "')"			

	try:
		# determine which statistical summary to provide
		if statistic == 'listing':
			fields = ['title', 'programTitle', 'airDateTime', 'duration', 'regionID']
			column_names = fields
			sql = "SELECT {} FROM starSchedule WHERE showid in (SELECT showid FROM favoriteshow WHERE userID = {}) AND {}".format(",".join(fields), id, date_clause)

		elif statistic == 'hour':
			fields = ['title', 'programTitle','SUM(duration) as hours', 'regionID']
			column_names = ['title', 'programTitle', 'hours', 'regionID']
		sql = "SELECT {} FROM starSchedule WHERE showid in (SELECT showid FROM favoriteshow WHERE userID = {}) AND {} GROUP BY title, regionID ".format(",".join(fields), id, date_clause)

		cur.execute(sql)
		result = cur.fetchall()
		conn.close()
		return Response(format(result,column_names), status=status.HTTP_200_OK)
	except psycopg2.ProgrammingError as e: 
		print (repr(e))
		conn.close()
		return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET', 'POST', 'DELETE'])
def favoriteShow(request):
	conn = getConnection()
	cur = conn.cursor()

	if request.method == 'GET':
		"""
		Get the showID and title of user's Favorite Shows
		"""
		key = request.path.split("favoriteshow/")[1].replace("/","")
		if len(key) == 0:
			return Response("No userID specified.", status=status.HTTP_400_BAD_REQUEST)
		try:
			fields = ['showID', 'title', 'showtype', 'ratingid', 'language']
			sql = "SELECT {} FROM favoriteshow JOIN show USING (showID) WHERE userID = \'{}\';".format(",".join(fields), key)
			cur.execute(sql)
			result = cur.fetchall()
			conn.close()
			return Response(format(result,fields), status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)

	else: # POST or DELETE

		id = request.data.get('userID')
		show = request.data.get('showID')
		if id == None or show == None:
			return Response("No userID or showID provided.", status=status.HTTP_400_BAD_REQUEST)
			
		if request.method == 'POST':
			"""
			Add a show to user's Favorite Shows
			"""
			try:
				# check if the show is already in the favorite list
				sql = "SELECT userID, showID FROM favoriteshow WHERE userID = \'{}\';".format(id)
				cur.execute(sql)
				currentShows = cur.fetchall()
				if (id, show) in currentShows:
					conn.close()
					return Response("This show is already in the user's favorite shows.", status=status.HTTP_400_BAD_REQUEST)
				
				# if not, add to the list
				sql = "INSERT INTO favoriteshow (userID, showID) VALUES (\'{}\', \'{}\')".format(id, show)
				cur.execute(sql)
				conn.commit()
				conn.close()
				return Response("The show has been added to user's favorite shows.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e: 
				print (repr(e))
				conn.close()
				return Response(status=status.HTTP_404_NOT_FOUND)

		if request.method == 'DELETE':
			"""
			Delete a show from user's Favorite Shows
			"""
			try:
				sql = "DELETE FROM favoriteshow WHERE userID = \'{}\' AND showID = \'{}\';".format(id, show)
				cur.execute(sql)
				conn.commit()
				conn.close()
				if cur.rowcount == 0:
					return Response("The userID/showID is invalid or the show has been removed", status=status.HTTP_400_BAD_REQUEST)
				return Response("The show has been deleted from user's favorite shows.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e: 
				print (repr(e))
				conn.close()
				return Response(status=status.HTTP_404_NOT_FOUND)

		

@api_view(['GET', 'POST', 'DELETE'])
def savedQuery(request):
	conn = getConnection()
	cur = conn.cursor()

	if request.method == 'GET':
		"""
		Get query and description of user's Saved Queries
		"""
		key = request.path.split("savedquery/")[1].replace("/","")
		if len(key) == 0:
			return Response("No userID specified.", status=status.HTTP_400_BAD_REQUEST)
		conn = getConnection()
		cur = conn.cursor()
		try:
			fields = ['query', 'description']
			sql = "SELECT {} FROM savedquery WHERE userID = \'{}\';".format(",".join(fields), key)
			cur.execute(sql)
			result = cur.fetchall()
			conn.close()
			return Response(format(result,fields), status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)

	else: # POST or DELETE

		id = request.data.get('userID')
		query = request.data.get('query')
		description = request.data.get('description') or query
		
		if id == None or query == None:
			conn.close()
			return Response("The userID/query/description is missing.", status=status.HTTP_400_BAD_REQUEST)
			
		if request.method == 'POST':
			"""
			Add a show to user's Saved Queries
			"""
			try:
				# check if the query is already in the saved list
				sql = "SELECT userID, query FROM savedquery WHERE userID = \'{}\';".format(id)
				cur.execute(sql)
				currentQueries = cur.fetchall()
				if (id, query) in currentQueries:
					conn.close()
					return Response("This query is already in the user's saved queries.", status=status.HTTP_400_BAD_REQUEST)	
				
				# if not, add it to the list
				sql = "INSERT INTO savedquery VALUES (\'{}\', \'{}\', \'{}\')".format(id, query, description)
				cur.execute(sql)
				conn.commit()
				conn.close()
				return Response("The query has been added to user's saved queries.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e: 
				print (repr(e))
				conn.close()
				return Response(status=status.HTTP_404_NOT_FOUND)
	
		
		if request.method == 'DELETE':
			"""
			Delete a query from user's Saved Queries
			"""
			try:
				sql = "DELETE FROM savedquery WHERE userID = \'{}\' AND query = \'{}\';".format(id, query)
				cur.execute(sql)
				conn.commit()
				conn.close()
				if cur.rowcount == 0:
					return Response("The userID/query is invalid or the query has been removed.", status=status.HTTP_400_BAD_REQUEST)
				return Response("The query has been deleted from user's saved query.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e: 
				print (repr(e))
				conn.close()
				return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def show(request):
	"""
	Get the showID given a particular show name.
	"""
	conn = getConnection()
	cur = conn.cursor()
	key = request.path.split("show/")[1].replace("/","")

	try:
		if len(key) == 0:
			conn.close()
			return Response("No show title specified.", status=status.HTTP_400_BAD_REQUEST)
		else:
			fields = ['showID', 'title']
			sql = "SELECT {} FROM show WHERE lower(title) LIKE '%{}%'".format(','.join(fields), key.replace('\'','\'\'').lower())
			cur.execute(sql)
			result = cur.fetchall()
			conn.close()
			if len(result) == 0:
				return Response("No showID found.", status=status.HTTP_400_BAD_REQUEST)
			return Response(format(result,fields), status=status.HTTP_200_OK)

	except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def menu(request):
	"""
	Get a list of distinct items for query fields, including show title, show type, region, and genre.
	"""
	conn = getConnection()
	cur = conn.cursor()
	key = request.path.split("menu/")[1].replace("/","")
	result_dic = {}

	# a dictionary to store the table and column name for a query field
	dic = {'region': ('region', 'regionID'), 'genre': ('genre', 'genre'), 'title': ('show', 'title'), 'showType': ('show', 'showType')}
	
	try:
		# if no field is specified, return distinct items for all available fields
		if len(key) == 0:
			for k, v in dic.items():
				sql = "SELECT DISTINCT {} FROM {} ORDER BY {};".format(v[1], v[0], v[1])
				cur.execute(sql)
				result = cur.fetchall()
				unlist = [item for sublist in result for item in sublist]
				result_dic[k] = unlist
			conn.close()
			return Response(result_dic, status=status.HTTP_200_OK)

		# find distinct items for the field specified
		else:
			lookup = dic.get(key)
			if lookup == None:
				conn.close()
				return Response("Invalid column name.", status=status.HTTP_400_BAD_REQUEST)
			table = lookup[0]
			column = lookup[1]
			sql = "SELECT DISTINCT {} FROM {} ORDER BY {};".format(column, table, column)
			cur.execute(sql)
			result = cur.fetchall()
			unlist = [item for sublist in result for item in sublist]
			conn.close()
			result_dic[key] = unlist
			return Response(result_dic, status=status.HTTP_200_OK)

	except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def program(request):
	"""
	Get all airing instances of TV programs matching given conditions.
	Query fields: 
	title: exact match of show title
	showType: exact match of show type 
	region: exact match of region 
	genre: exact match of genre 
	dateFrom: airDateTime starting from the given date
	dateTo: airDateTime starting by the given date
	timeFrom: airDateTime starting from the given time (hour 0-23)
	timeTo: airDateTime starting by the given time (hour 0-23)
	keyword: wildcard search in the program's title and description
	orderBy: order results by column(s)
	"""
	conn = getConnection()
	cur = conn.cursor()
	fields = ['showID', 'title', 'programTitle', 'showType', 'airDateTime', 'duration', 'stationName', 'regionID', 'contentRatingId', 'language', 'description', 'castcrew', 'programRatingId', 'scheduleRatingID', 'status', 'originalAirDate']

	try:
		# extract and validate the query conditions that user specified
		conditions = []
		orderBy = 'title'
		timeComplete = False;
		dateComplete = False;
		for key, value in request.data.items():

			# query by time (hour)
			if key in ('timeFrom', 'timeTo'):
				if timeComplete == True:
					continue
				timeFrom = request.data.get('timeFrom') or 0
				timeTo = request.data.get('timeTo') or 24

				# timeFrom > timeTo (overnight)
				if timeFrom > timeTo:
					conditions.append("date_part(h, airDateTime) >= " + timeFrom + "OR date_part(h, airdatetime) <= " + timeTo)
				
				# timeFrom <= timeTo (regular)
				elif timeFrom <= timeTo:
					conditions.append("date_part(h, airDateTime) BETWEEN " + timeFrom + " AND " + timeTo)
				
				# flip the flag
				timeComplete == True

			# query by date
			elif key in ('dateFrom', 'dateTo'):
				if dateComplete == True:
					continue
				# default dateFrom value is today
				dateFrom = request.data.get('dateFrom') or str(DT.date.today())
				# default dateFrom value is dateFrom + 14 days
				dateTo = request.data.get('dateTo') or str((DT.datetime.strptime(dateFrom, '%Y-%m-%d') + DT.timedelta(days=14)).date())

				# check if time range is valid
				if dateFrom > dateTo:
					conn.close()
					return Response("Invalid date range.", status=status.HTTP_400_BAD_REQUEST)
				
				conditions.append("airDateTime BETWEEN '" + dateFrom + "' AND dateadd(day,1,'" + dateTo + "')")
				
				# flip the flag
				dateComplete == True

			# query by keyword
			elif key == 'keyword':
				words = re.split('\s|[,.]', value)
				for word in words:
					word = word.lower().replace('\'','\'\'')
					temp = "lower(title) LIKE '%" + word + "%' OR lower(description) LIKE '%" + word + "%'"
					conditions.append(temp)

			# orderBy by columns
			elif key == 'orderBy':
				columns = re.split('\s|[,.]', value)
				orderBy = ",".join(columns)

			# other query fields	
			else:	
				conditions.append(key + " = '" + value.replace('\'','\'\'') + "'")
	
		# run the query
		if len(conditions) == 0:
			sql = "SELECT {} FROM starSchedule ORDER BY {}".format(",".join(fields), orderBy)
		else:
			sql = "SELECT {} FROM starSchedule WHERE {} ORDER BY {}".format(",".join(fields), " AND ".join(conditions), orderBy)
		cur.execute(sql)
		result = cur.fetchall()
		conn.close()
		return Response(format(result,fields), status=status.HTTP_200_OK)	

	except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.close()
			return Response(status=status.HTTP_404_NOT_FOUND)
	
				

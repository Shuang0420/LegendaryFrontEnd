# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# views.py

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psycopg2


# Obtain connection to Redshift
def getConnection():
	conn = psycopg2.connect(
		dbname='cmucapstonejd',
		port='5439',
		user='cmucapstonejd',
		password='Ngl91dY2daIa3wFD1QhL',
		host='cmucapstone.cjvi8xu2ejaw.us-east-2.redshift.amazonaws.com'
		)
	return conn



# Format a query result (a list of tuples) to a JSON string
# @rows: a list of sql results in tuples
# @fields: a list of column names
def format(rows, fields):
	try:
		if rows == None or fields == None:
			raise ValueError('Null input')
		if len(rows) == 0:
			return ""
		if len(rows[0]) != len(fields):
			raise ValueError('Inconsistent field lengths')
		dicts = (dict(zip(fields,row)) for row in rows)
		return dicts
	except ValueError as err:
		return (err)


# Get or update user information
@api_view(['GET', 'POST'])
def user(request):
	conn = getConnection()
	cur = conn.cursor()
	if request.method == 'GET':
		key = request.path.split("user/")[1].replace("/","")
		try:
			if len(key) == 0:
				fields = ['userID', 'name']
				sql = "SELECT {} FROM userinfo ORDER BY userID;".format(",".join(fields))
				cur.execute(sql)
				result = cur.fetchall()
				conn.close();
				return Response(format(result,fields), status=status.HTTP_200_OK)
			else :
				fields = ['name', 'password']
				sql = "SELECT {} FROM userinfo WHERE userID = \'{}\';".format(",".join(fields), key)
				cur.execute(sql)
				result = cur.fetchall()
				conn.close();
				if len(result) == 0:
					return Response("Invalid userID.", status=status.HTTP_404_NOT_FOUND)
				return Response(format(result,fields), status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e:
			print (repr(e))
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)

	elif request.method == 'POST':
		id = request.data.get('userID')
		pd = request.data.get('password')
		if id == None or pd == None:
			return Response("No userID or/and password provided.", status=status.HTTP_400_BAD_REQUEST)
		try:
			sql = "UPDATE userinfo SET password = \'{}\' WHERE userID = \'{}\';".format(pd,id)
			cur.execute(sql)
			conn.commit();
			conn.close();
			if cur.rowcount == 0:
				return Response("Invalid userID.", status=status.HTTP_404_NOT_FOUND)
			return Response("Password has been updated.", status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e:
			print (repr(e))
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)



# Add a show to or delete from User's Favorite Shows
@api_view(['GET', 'POST', 'DELETE'])
def favoriteShow(request):

	if request.method == 'GET':
		key = request.path.split("favoriteshow/")[1].replace("/","")
		if len(key) == 0:
			return Response("No userID specified.", status=status.HTTP_400_BAD_REQUEST)
		conn = getConnection()
		cur = conn.cursor()
		try:
			fields = ['showID', 'title']
			sql = "SELECT {} FROM favoriteshow JOIN show USING (showID) WHERE userID = \'{}\';".format(",".join(fields), key)
			cur.execute(sql)
			result = cur.fetchall()
			conn.close();
			if len(result) == 0:
				return Response("User has no favorite shows yet.", status=status.HTTP_200_OK)
			return Response(format(result,fields), status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e:
			print (repr(e))
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)
	else:
		id = request.data.get('userID')
		show = request.data.get('showID')
		conn = getConnection()
		cur = conn.cursor()
		if id == None or show == None:
			return Response("No userID or showID provided.", status=status.HTTP_400_BAD_REQUEST)

		if request.method == 'POST':
			try:
				sql = "SELECT userID, showID FROM favoriteshow WHERE userID = \'{}\';".format(id)
				cur.execute(sql)
				currentShows = cur.fetchall()
				if (id, show) in currentShows:
					conn.close();
					return Response("This show is already in the user's favorite shows.", status=status.HTTP_200_OK)
				sql = "INSERT INTO favoriteshow (userID, showID) VALUES (\'{}\', \'{}\');".format(id, show)
				cur.execute(sql)
				conn.commit();
				conn.close();
				if cur.rowcount == 0:
					return Response("Invalid userID/showID.", status=status.HTTP_404_NOT_FOUND)
				return Response("The show has been added to user's favorite shows.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e:
				print (repr(e))
				conn.close();
				return Response(status=status.HTTP_404_NOT_FOUND)

		if request.method == 'DELETE':
			try:
				sql = "DELETE FROM favoriteshow WHERE userID = \'{}\' AND showID = \'{}\';".format(id, show)
				cur.execute(sql)
				conn.commit();
				conn.close();
				if cur.rowcount == 0:
					return Response("Invalid userID/showID.", status=status.HTTP_404_NOT_FOUND)
				return Response("The show has been deleted from user's favorite shows.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e:
				print (repr(e))
				conn.close();
				return Response(status=status.HTTP_404_NOT_FOUND)



# Add a query to or delete from User's Saved Queries
@api_view(['GET', 'POST', 'DELETE'])
def savedQuery(request):

	if request.method == 'GET':
		key = request.path.split("savedquery/")[1].replace("/","")
		if len(key) == 0:
			return Response("No userID specified.", status=status.HTTP_400_BAD_REQUEST)
		conn = getConnection()
		cur = conn.cursor()
		try:
			fields = ['query', 'queryDes']
			sql = "SELECT {} FROM savedquery WHERE userID = \'{}\';".format(",".join(fields), key)
			cur.execute(sql)
			result = cur.fetchall()
			conn.close();
			if len(result) == 0:
				return Response("User has no saved queries yet.", status=status.HTTP_200_OK)
			return Response(format(result,fields), status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e:
			print (repr(e))
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)
	else:
		id = request.data.get('userID')
		query = request.data.get('query')
		description = request.data.get('description')
		conn = getConnection()
		cur = conn.cursor()
		if id == None or query == None:
			return Response("No userID or query provided.", status=status.HTTP_400_BAD_REQUEST)

		if request.method == 'POST':
			try:
				sql = "SELECT userID, query FROM savedquery WHERE userID = \'{}\';".format(id)
				cur.execute(sql)
				currentQueries = cur.fetchall()
				if (id, query) in currentQueries:
					conn.close();
					return Response("This query is already in the user's saved queries.", status=status.HTTP_200_OK)
				sql = "INSERT INTO savedquery VALUES (\'{}\', \'{}\');".format(id, query, description)
				cur.execute(sql)
				conn.commit();
				conn.close();
				if cur.rowcount == 0:
					return Response("Invalid userID/showID.", status=status.HTTP_404_NOT_FOUND)
				return Response("The query has been added to user's saved queries.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e:
				print (repr(e))
				conn.close();
				return Response(status=status.HTTP_404_NOT_FOUND)

		if request.method == 'DELETE':
			try:
				sql = "DELETE FROM savedquery WHERE userID = \'{}\' AND query = \'{}\';".format(id, query)
				cur.execute(sql)
				conn.commit();
				conn.close();
				if cur.rowcount == 0:
					return Response("Invalid userID/showID.", status=status.HTTP_404_NOT_FOUND)
				return Response("The query has been deleted from user's saved query.", status=status.HTTP_200_OK)
			except psycopg2.ProgrammingError as e:
				print (repr(e))
				conn.close();
				return Response(status=status.HTTP_404_NOT_FOUND)


# Get a list of distinct items for query fields, including program title, region, and genre.
@api_view(['GET'])
def menu(request):
	conn = getConnection()
	cur = conn.cursor()
	key = request.path.split("menu/")[1].replace("/","")
	result_dic = {}
	# a dictionary to store the table and column name of a query field
	dic = {'region': ('region', 'regionID'), 'genre': ('genre', 'genre'), 'show': ('show', 'title')}
	try:
		if len(key) == 0:
			for k, v in dic.items():
				sql = "SELECT DISTINCT {} FROM {} ORDER BY {};".format(v[1], v[0], v[1])
				cur.execute(sql)
				result = cur.fetchall()
				unlist = [item for sublist in result for item in sublist]
				result_dic[k] = unlist
			conn.close();
			return Response(result_dic, status=status.HTTP_200_OK)
		else:
			table = dic.get(key)[0]
			column = dic.get(key)[1]
			sql = "SELECT DISTINCT {} FROM {} ORDER BY {};".format(column, table, column)
			cur.execute(sql)
			result = cur.fetchall()
			unlist = [item for sublist in result for item in sublist]
			if len(unlist) == 0:
				return Response("Invalid column name.", status=status.HTTP_404_NOT_FOUND)
			result_dic[key] = unlist
			return Response(result_dic, status=status.HTTP_200_OK)
	except psycopg2.ProgrammingError as e:
			print (repr(e))
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def program(request):
#    return Response('GET programs not implemented yet', status=status.HTTP_200_OK)
		print "Step1"
		# request)
		conn = getConnection()
		cur = conn.cursor()
		dict = {'programid': 'PROGRAM', 'description': 'PROGRAM', 'showid': 'PROGRAM', 'castcrew': 'PROGRAM', 'ratingid': 'PROGRAM', 'language': 'PROGRAM', 'castcrew': 'PROGRAM','scheduleid': 'SCHEDULE', 'stationid': 'SCHEDULE', 'programid': 'SCHEDULE', 'airdatetime': 'SCHEDULE', 'duration': 'SCHEDULE', 'ratingid': 'SCHEDULE', 'isnew':'SCHEDULE', 'showid':'SHOW', 'title':'SHOW', 'originalairdate':'SHOW', 'showtype':'SHOW', 'ratingid':'SHOW', 'language':'SHOW', 'stationid':'STATION','stationname':'STATION','affiliate':'STATION','logurl':'STATION','language':'STATION','broadcastRegionID':'STATION','ratingID':'RATING','code':'RATING', 'body':'RATING','regionID':'REGION','country':'REGION','state':'REGION','city':'REGION','zip':'REGION'}
		caseListCondition = []
		caseListColumn = []
		caseListTable = []

		for key, value in request.GET.items():
			print "key value pair" + str(key) + "-->"+str(value)
			caseListCondition.append("'"+value.lower()+"'")
			caseListColumn.append(key.lower())
			caseListTable.append(dict[key.lower()])
		length = len(caseListColumn)

		for object in caseListCondition, caseListColumn, caseListTable:
			print(object)

		try:
			"""
			if caseListColumn[0] == 'title':
			#cur.execute(" Select showname FROM shows where "  + caseListColumn[0] +  " = " +  caseListCondition[0] + " AND " + caseListColumn[1] + " = " + caseListCondition[1])
			#cur.execute(" Select showname FROM shows where \'{}\' = \'{}\' AND \'{}\' = \'{}\'".format(caseListColumn[0], caseListCondition[0], caseListColumn[1], caseListCondition[1]))
			#print(" Select title FROM show where {} = \'{}\' AND {} = \'{}\'".format(caseListColumn[0], caseListCondition[0], caseListColumn[1], caseListCondition[1]))
			#cur.execute(" Select title FROM show where {} = \'{}\' AND {} = \'{}\'".format(caseListColumn[0], caseListCondition[0], caseListColumn[1], caseListCondition[1]))
				fields = ['showID', 'title', 'originalAirDate', 'showType', 'ratingID', 'language']
				cur.execute(" Select {} FROM show where {} = \'{}\' AND {} = \'{}\'".format(",".join(fields), caseListColumn[0], caseListCondition[0], caseListColumn[1], caseListCondition[1]))

			"""
			fields = ["Title", "Showtype", "Description", "StationName", "airdatetime", "Duration"]
			#query = 'SELECT {} FROM schedule WHERE  programid IN (SELECT programid from program WHERE showid IN (select showid from show where LOWER(title) = {}))'.format(",".join(fields),caseListCondition[0].lower())
			query = "SELECT show.title, showtype, description, stationName, airdatetime, duration \
			         FROM schedule LEFT OUTER JOIN program ON schedule.programID = program.programID\
					 LEFT OUTER JOIN station ON station.stationID = schedule.stationID\
					 LEFT OUTER JOIN show ON show.showID = program.showID\
					 WHERE LOWER(show.title) = {};".format(caseListCondition[0])

			print query
			cur.execute(query)

			result = cur.fetchall()
			print "RESULT = " + str(result)
			return Response(format(result,fields), status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as exc:
			print(exc)
			return Response(status=HTTP_400_BAD_REQUEST)

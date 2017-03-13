# views.py

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psycopg2


# Obtain connection to RedShift
def getConnection(): 

	connenction_string = "dbname='cmucapstonejd' port='5439' user='cmucapstonejd' password='Ngl91dY2daIa3wFD1QhL' host='cmucapstone.cvtax4qegotm.us-west-2.redshift.amazonaws.com'";
	conn = psycopg2.connect(connenction_string)
	return conn


# Get or update user information
@api_view(['GET', 'POST'])
def user(request):

	if request.method == 'GET':
		field = request.path.split("user/")[1].replace("/","")
		if len(field) == 0:
			return Response("No userID specified.", status=status.HTTP_400_BAD_REQUEST)
		conn = getConnection()
		cur = conn.cursor()
		try:
			sql = "SELECT name, password FROM users WHERE userID = \'{}\';".format(field)
			cur.execute(sql)
			result = cur.fetchall()
			conn.commit();
			conn.close();
			if len(result) == 0:
				return Response("Invalid userID.", status=status.HTTP_404_NOT_FOUND)
			return Response(result, status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.commit();
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)

	elif request.method == 'POST':
		id = request.data.get('userID')
		pd = request.data.get('password')
		conn = getConnection()
		cur = conn.cursor()
		if id == None or pd == None:
			return Response("No userID or/and password provided.", status=status.HTTP_400_BAD_REQUEST)
		print(id+", "+ pd)
		try:
			sql = "UPDATE users SET password = \'{}\' WHERE userID = \'{}\';".format(pd,id)
			cur.execute(sql)
			print(cur.rowcount)
			conn.commit();
			conn.close();
			if cur.rowcount == 0:
				return Response("Invalid userID.", status=status.HTTP_404_NOT_FOUND)
			return Response("Password has been updated.", status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.commit();
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)



# Add a show to or delete from User's Favorite Shows
@api_view(['GET', 'PUT', 'DELETE'])
def favoriteShows(request):

	if request.method == 'GET':
		field = request.path.split("favoriteShows/")[1].replace("/","")
		if len(field) == 0:
			return Response("No userID specified.", status=status.HTTP_400_BAD_REQUEST)
		conn = getConnection()
		cur = conn.cursor()
		try:
			sql = "SELECT f.programID, p.title FROM favoriteshows f JOIN programs p USING (programID) WHERE userID = \'{}\';".format(field)
			cur.execute(sql)
			result = cur.fetchall()
			conn.commit();
			conn.close();
			if len(result) == 0:
				return Response("User has no favorite shows yet.", status=status.HTTP_200_OK)
			return Response(result, status=status.HTTP_200_OK)
		except psycopg2.ProgrammingError as e: 
			print (repr(e))
			conn.commit();
			conn.close();
			return Response(status=status.HTTP_404_NOT_FOUND)

	elif request.method == 'PUT':
		return Response('PUT favoriteShows not implemented yet', status=status.HTTP_200_OK)

	elif request.method == 'DELETE':
		return Response('DELETE favoriteShows not implemented yet', status=status.HTTP_200_OK)
	


# Add a query to or delete from User's Saved Queries
@api_view(['GET', 'PUT', 'DELETE'])
def savedQueries(request):

	if request.method == 'GET':
		return Response('GET savedQueries not implemented yet', status=status.HTTP_200_OK)

	elif request.method == 'PUT':
		return Response('PUT savedQueries not implemented yet', status=status.HTTP_200_OK)

	elif request.method == 'DELETE':
		return Response('DELETE savedQueries not implemented yet', status=status.HTTP_200_OK)



# Get a list of distinct items for query fields, including program title, region, and genre.
@api_view(['GET'])
def menu(request):
    return Response('GET menu not implemented yet', status=status.HTTP_200_OK)



@api_view(['GET'])
def programs(request):
    return Response('GET programs not implemented yet', status=status.HTTP_200_OK)



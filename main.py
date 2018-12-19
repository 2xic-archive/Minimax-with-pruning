#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import send_from_directory
from flask import Flask, request
from flask import jsonify
from minmax import *
from board import *
import json
import os

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'frontend') + "/"
app = Flask(__name__, static_url_path='')

currentBoard = board()

#	Route the main file
@app.route('/')
def index():
	return send_from_directory(static_file_dir, 'checkers.html')

#	Main file need a route for script + css
@app.route('/<path>')
def statics(path):
	return send_from_directory(static_file_dir, path)

#	To verify that the game is still playable
@app.route('/state', methods=['POST']) 
def remove():
	global currentBoard
	return jsonify(state = ("done" if (currentBoard.cantMove()) else "notDone"))

#	Return the state of the board
@app.route('/reset', methods=['POST']) 
def reset():
	global currentBoard
	playerCordinates= [[], []]
	currentBoard = board()
	players = [list(currentBoard.playerRed.values()), list(currentBoard.playerBlack.values())]
	for player in range(0, len(players)):
		for piece in players[player]:
			playerCordinates[player].append(str(piece[0]) + "-" + str(piece[1]))

	return jsonify(
		playerBlack=playerCordinates[0],
		playerRed=playerCordinates[1],
		boardSize=currentBoard.boardSize
	)

#	Do a move on the board
@app.route('/boardmove', methods=['POST']) 
def humanMove():
	global currentBoard
	moveFrom = (int(request.json["from"][0]), int(request.json["from"][1]))
	moveTo = (int(request.json["to"][0]), int(request.json["to"][1]))

	if(len(currentBoard.playerBlack.keys()) == 0 or len(currentBoard.playerRed.keys()) == 0):
		return jsonify(
				state="done"
		)
	elif(moveFrom in list(currentBoard.playerBlack.values())):
		currentBoard.makeMove(moveFrom, moveTo)
		#	The minimax tree will only look for aggressive moves in the "future"
		currentBoard.aggressivePlayer = -1
		computerMove = getComputerMove(currentBoard)
		currentBoard =  computerMove[0]		

		if((currentBoard.cantMove()) and computerMove[2] == None):
			return jsonify(state="done")	
		elif(currentBoard.cantMove() and computerMove[2] != None):
			return jsonify(
				state="done",
				positonold=computerMove[2][0],
				positonnew=computerMove[2][1])	
		else:	
			return jsonify(
				state="game",
				positonold=computerMove[2][0],
				positonnew=computerMove[2][1]
			)
	else:
		raise Exception("Something went wrong.")

if __name__ == '__main__':
	app.run(debug=True)


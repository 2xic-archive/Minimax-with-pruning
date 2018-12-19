#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import deepcopy
import math

def getComputerMove(board):
	bestBoard = None 
	currentDepth = board.treeDepth# +1
	while not bestBoard and currentDepth > 0:
		(bestBoard, bestVal, bestMove) = maxMove2(board, currentDepth)
		currentDepth -= 1
		print(bestVal)
	if not bestBoard:
		raise Exception("Could only return null boards")
	else:
		return (bestBoard, bestVal, bestMove)

def maxMove2(maxBoard, currentDepth, alpha=float('-inf'), beta=float('inf'), best_move_type=None):
	#	Finding the best move for the computer  (red)
	return maxMinBoard(maxBoard, currentDepth-1, float('-inf'), alpha, beta, best_move_type)
	
def minMove2(minBoard, currentDepth, alpha=float('-inf'), beta=float('inf'), best_move_type=None):
	#	Finding best move for human player      (black)
	return maxMinBoard(minBoard, currentDepth-1, float('inf'), alpha, beta, best_move_type)

def aggresivMove(board):
	return (board.mode == board.aggressiveMode and board.aggressivePlayer != -1)

def maxMinBoard(board, currentDepth, bestMove, alpha, beta, best_move_type):
	if aggresivMove(board) or currentDepth <= 0:
		return (board, evalBoard(board), best_move_type)

	best_move = bestMove
	best_board = None    

	if bestMove == float('-inf'):
		#	Checking the moves
		moves = board.getMoves(board.playerRed)
		for (moveFrom, moveTo) in moves:
			maxBoard = deepcopy(board)
			maxBoard.makeMove(moveFrom, moveTo)
			value = minMove2(maxBoard, currentDepth-1, alpha, beta, best_move_type)[1]

			#	Alpha-beta pruning
			alpha = max(alpha, value)
			if value > best_move:
				best_move = value
				best_board = maxBoard         
				best_move_type = (moveFrom, moveTo)
			
			if alpha >= beta:
				break
	elif bestMove == float('inf'):
		#	Checking the moves
		moves = board.getMoves(board.playerBlack)
		for (moveFrom, moveTo) in moves:
			minBoard = deepcopy(board)
			minBoard.makeMove(moveFrom, moveTo)
			value =  maxMove2(minBoard, currentDepth-1, alpha, beta, best_move_type)[1]

			# Alpha-beta pruning
			beta = min(beta, value)
			if value < best_move:
				best_move = value
				best_board = minBoard
				best_move_type = (moveFrom, moveTo)

			if alpha >= beta:
				break
	else:
		raise Exception("bestMove is set to something other than inf or -inf")

	return (best_board, best_move, best_move_type)

#	Calculate a score of the board state 
def evalBoard(currentBoard):
	#	The player that did the last move
	challengingPlayer = None 
	challengingKings = None 
	#	The player that now has to do a move
	turnPlayer = None 
	turnKings = None
	#	Black wants -inf and red wants inf
	scoremod = None
	
	#	Aggressive moves will give max score
	if(currentBoard.aggressivePlayer == currentBoard.blackID and currentBoard.mode == currentBoard.aggressiveMode):
		return float('-inf')
	elif(currentBoard.aggressivePlayer == currentBoard.redID and currentBoard.mode == currentBoard.aggressiveMode):
		return float('inf')

	if(currentBoard.turn == currentBoard.blackID):
		turnPlayer = list(currentBoard.playerBlack.values())
		challengingPlayer = list(currentBoard.playerRed.values())
		
		challengingKings = currentBoard.kings["red"]
		turnKings = currentBoard.kings["black"]
		scoremod = -1
	else:
		turnPlayer = list(currentBoard.playerRed.values())
		challengingPlayer = list(currentBoard.playerBlack.values())
		
		challengingKings = currentBoard.kings["black"]
		turnKings = currentBoard.kings["red"]
		scoremod = 1

	'''
	Super Gigadeath Defense Evaluator
	This agent will attempt to keep it's peices as close together as possible until it has a chance
	to jump the opposing player. It's super effective
	'''
	distance = 0
	for piece1 in turnPlayer:
		for piece2 in turnPlayer:
			if piece1 == piece2:
				continue
			dx = abs(piece1[0] - piece2[0])
			dy = abs(piece1[1] - piece2[1])
			distance += dx**2 + dy**2

	distance = 1 if(distance == 0) else distance/len(turnPlayer)
	kingRatio =  ((len(turnKings) + 1) / (len(challengingKings) + 1))
	playerRatio = ((len(turnPlayer) + 1) / (len(challengingPlayer) + 1))
	score = math.sqrt(distance) * kingRatio * playerRatio

	return scoremod * float(1 / (1 + math.exp(-math.sqrt(score))))



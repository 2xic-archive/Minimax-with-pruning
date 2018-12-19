#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import deepcopy

class board(object):
	#	Player id's
	blackID = 1
	redID = 0
	#	Game modes
	normalMode = 0
	aggressiveMode = 1
	def __init__(self):
		self.boardSize = 8

		self.playerRed = {

		}
		self.playerBlack = {

		}
		self.kings = {
			"black":[],
			"red":[]
		}

		#	Set the coordinates of the pieces
		for i in range(self.boardSize):
			self.playerRed[i] = ((i, (i + 1) % 2))
			self.playerBlack[i + self.boardSize] = (i, self.boardSize - (i % 2) - 1)
		#	First move is played by the human
		self.turn = self.blackID
		'''
			Higher depth (should) equal better moves, but at the cost of cpu time.
			However by using aggressive mode, you can "restore" some of that cpu time, 
			but the moves played might not be as good. The reason for this is because a 
			piece will take the other players piece if it can regardless of the board state.
		'''
		self.treeDepth = 10
		self.mode = self.aggressiveMode
		self.aggressivePlayer = -1

	def cantMove(self):
		movesBlack = 0
		movesRed = 0

		for i in self.getMoves(self.playerBlack):
			movesBlack += 1
			break

		for i in self.getMoves(self.playerRed):
			movesRed += 1
			break

		return (movesRed <= 0 or movesBlack <= 0)
		
	def getMoves(self, player):
		for PieceID, piece in (player.items()):
			if(player == self.playerBlack):
				for move in self.movesBlack(piece, PieceID):
					yield move
			else:
				for move in self.movesRed(piece, PieceID):
					yield move
				
	def movesBlack(self, piece, PieceID):
		return self.moveGeneration(piece, [(-1,-1),(1,-1)], PieceID)
	
	def movesRed(self, piece, PieceID):
		return self.moveGeneration(piece, [(-1,1),(1,1)], PieceID)

	def outsideBoard(self, x, y):
		return not ((0 <= x < self.boardSize) and (0 <= y < self.boardSize))
	
	def legalMoves(self, piecexy, move):
		#	Can't move to a tile if it's occupied
		def tileEmty(target):
			return (target in list(self.playerRed.values())), (target in list(self.playerBlack.values()))

		def getNewPosition(piecexy, move):
			targetx = piecexy[0] + move[0] 
			targety = piecexy[1] + move[1] 
			if(self.outsideBoard(targetx, targety)):
				raise ValueError("out of border")
			return (targetx, targety)

		nextMove = getNewPosition(piecexy, move)
		redPiece, blackPiece = tileEmty(nextMove)
			
		if not blackPiece and not redPiece:
			return (piecexy, nextMove)

		#	There is a piece in the way. Jump is only possible if the piece is of opposite color
		if (self.turn == self.blackID and blackPiece) or (self.turn == self.redID and redPiece):
			raise ValueError("Illegal jump")

		nextMove = getNewPosition(nextMove, move)
		redPiece, blackPiece = tileEmty(nextMove)
		if not blackPiece and not redPiece:
			return (piecexy, nextMove)
		else:
			raise ValueError("Illegal jump")


	def moveGeneration(self, piecexy, moves, PieceID):
		#	When a piece have gone to the opposite side of the board it becomes a king
		if(PieceID in self.kings["black"] or PieceID in self.kings["red"]):
			for move in deepcopy(moves):
				moves.append((-move[0], -move[1]))
	
		#	Return valid moves
		for move in moves:
			try:
				validmove = self.legalMoves(piecexy, move)
				yield validmove
			except ValueError as e:
				pass

	#	Movement of pieces
	def makeMove(self, moveFrom, moveTo):
		if(self.outsideBoard(moveTo[0], moveTo[1])):
			raise Exception("That would move the piece out of the board")
		
		black = moveTo in list(self.playerRed.values())
		red = moveTo in list(self.playerBlack.values())
		if not (black or red):
			#	Updating the player list with new cordinates
			player = (self.playerRed if(self.turn == self.redID) else self.playerBlack)
			pieceIndex = list(player.values()).index(moveFrom)
			pieceID = list(player.keys())[pieceIndex]      
			player[pieceID] = moveTo
			
			#	If the move was a jump, remove the piece that got captured.
			if(abs(moveFrom[0]-moveTo[0]) == 2):
				#	The player did a move that was considered aggressive.
				self.aggressivePlayer = self.turn
				'''
				O = Old location of the "jumper"
				J = Piece getting captured
				N = New location of the "jumper"

				[0][0]
				-|-|-N-
				-|-J-|-
				-|O|-|-

				[0][1]
				-|O|-|-
				-|-J-|-
				-|-|N|-

				[1][0]
				-|N|-|-
				-|-J-|-
				-|-|O|-

				[1][1]
				-|-|O|-
				-|-J-|-
				-|N|-|-
				'''
				movematrix = [
						[[moveTo[0]-1, moveTo[1]+1], [moveTo[0]-1, moveTo[1]-1]],
						[[moveTo[0]+1, moveTo[1]+1], [moveTo[0]+1, moveTo[1]-1]]
				]

				DirectionX = 0 if((moveTo[0] - moveFrom[0]) > 0) else 1
				DirectionY = 0 if((moveTo[1] - moveFrom[1]) < 0) else 1

				attackedPiece = movematrix[DirectionX][DirectionY]
				reversePlayer = (self.playerRed if(self.turn == self.blackID) else self.playerBlack)
				getPieceIndex = list(reversePlayer.values()).index((attackedPiece[0], attackedPiece[1]))
				piece = list(reversePlayer.keys())[getPieceIndex]
				reversePlayer.pop(piece, None)

			#	Checking if the player has moved to the opposite side, if that's the case the piece will become king.
			if(	((moveTo[1] == 0 and self.turn == self.blackID))):
				if pieceID not in self.kings["black"]:
					self.kings["black"].append(pieceID)
			if((moveTo[1] == (self.boardSize-1) and self.turn == self.redID)):
				if pieceID not in self.kings["red"]:
					self.kings["red"].append(pieceID)
			#	Switch turns. 
			self.turn = int(bool(self.turn) == False)
		else:
			raise Exception("Illegal move")



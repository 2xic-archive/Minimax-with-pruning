
//	The piece that is currently selected
var activPiece = undefined;
	
//	List of tiles that are "active", the currently selected piece can move there.
var activeTiles = {

};
	
//	Has the computer done a move?
function isBoardFrozen(){
	return parseInt(document.getElementById("board").getAttribute("blackTurn")) == 1;
}

/*	
	"Freeze" the board so that the human player can't move while the agent is thinking.	
	"Un-freeze" the board so that the human can make a move again.
*/

function freezeBoard(state){
	return parseInt(document.getElementById("board").setAttribute("blackTurn", (!state | 0)));
}

//	Deactivate all the active tiles
function deactivateTiles(){
	Object.keys(activeTiles).forEach(function(key) {
		var value = activeTiles[key];
		document.getElementsByName(value)[0].style = "";
	});
	activeTiles = {};
}

//	Return the new coordinates if the move is legal, else -1
function legalMove(x, movementX, y, movementY){
	//	Check that the new coordinates is inside the board
	function outsideBoard(localSize){
		var boardSize = parseInt(document.getElementById("board").getAttribute("size"));
		return !((0 <= localSize) && (localSize < boardSize));
	}

	if(outsideBoard(x + movementX) || outsideBoard(y + movementY)){
		return -1;
	}

	var tile = document.getElementsByName((x + movementX) + "-" + (y + movementY))[0];
	var jump = (!outsideBoard(x + (2 * movementX)) && !outsideBoard(y + (2 * movementY)) && isBoardFrozen());
	/*
		Check that the new tile/coordinate does not already contain a piece 
		if that is the case, check if the player can jump over the piece.
	*/
	if(isBoardFrozen() && (tile.children.length == 0)){
		return [x + movementX, y + movementY];
	}else if(jump){
		//	check that the piece that is getting jumped over is not our own
		if(tile.children[0].getAttribute("black") == "false"){
			return [x + (2 * movementX), y + (2 * movementY)];
		}
	}
	return -1;
}

//	Checking that there still are playable moves 
function movesLeft(){
	fetch('/state', {
		method: 'POST',
		headers:{
			'Content-Type': 'application/json'
		}
	}).then(function(response) {
		return response.text();
	}).then(function(response) {
		var moveit = JSON.parse(response);
		if(moveit["state"] == "done"){
			document.getElementById("status").innerHTML = "Game is done";
			freezeBoard(true);
		}
	});
}

//	Get the playable tiles for a given piece
function getPlayableTiles(player){
	if(player.getAttribute("black") == "true"){
		deactivateTiles();

		function noChild(element){
			return (element != undefined && element.children.length == 0);
		}
		//	Only enable tile, if it is empty
		function validateTile(cordinates, tileid){
			if(noChild(document.getElementsByName(cordinates)[0])) {
				document.getElementsByName(cordinates)[0].style.background = "black";		
				activeTiles[tileid] = cordinates;
			}				
		}

		var currentX = parseInt(player.getAttribute("x"));
		var currentY = parseInt(player.getAttribute("y"));	
		// Verify the "legality" of the moves
		var avaibleMoves = [
			[	legalMove(currentX, +1, currentY, -1)	],	//	Front-left
			[	legalMove(currentX, -1, currentY, -1)	],	//	Front-right
			[	legalMove(currentX, +1, currentY, +1)	],	//	Back-left
			[	legalMove(currentX, -1, currentY, +1)	]	//	Back-right
		];
		// Enable tiles for moves that are legal
		for(var x = 0; x < avaibleMoves.length; x++){
			var newstate = avaibleMoves[x][0];
			if(newstate == -1){
				continue;
			}
			if((newstate[1]-currentY) > 0 && player.getAttribute("moveback") == undefined){
				break;
			}
			var cordinate = newstate[0] + "-" + newstate[1];
			validateTile(cordinate, x);
		}
		activPiece = player;
	}
}

//	Return the piece that is getting jumped over
function getJumptedPiece(newCoordinates, x, y){
	/*
			O = Old coordinates of the "jumper"
			J = The piece that is getting jumped over
			N = New coordinates of "jumper"

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
	*/
	var moveMatrix = [
			[	[newCoordinates[0]-1, newCoordinates[1]+1], [newCoordinates[0]-1,	newCoordinates[1]-1] ],
			[	[newCoordinates[0]+1,	newCoordinates[1]+1], [newCoordinates[0]+1,	newCoordinates[1]-1] ]
		];

	var directionX = (x > 0) ? 0 : 1;
	var directionY = (y < 0) ? 0 : 1;

	//	Get the relevant move 
	var move = moveMatrix[directionX][directionY];
	var coordinates = (move[0]) + "-" + (move[1]);
	return document.getElementsByName(coordinates)[0];
}

function checkIfJump(tile){
	if( Math.abs(parseInt(activPiece.getAttribute("x")) - parseInt(tile.getAttribute("x"))) == 2 ){	
		function coordinates(element, direction, tile=undefined){
			if(tile != undefined){
				return (parseInt(tile.getAttribute(direction)) - parseInt(element.getAttribute(direction)));
			}
			return parseInt(element.getAttribute(direction));
		}
		//	Getting the new coordinates of the piece
		var deltaX = coordinates(activPiece, "x", tile);
		var deltaY = coordinates(activPiece, "y", tile);
		var newcodinates = [coordinates(tile, "x"), coordinates(tile, "y")];

		var node = getJumptedPiece(newcodinates, deltaX, deltaY);
		node.removeChild(node.firstChild);

		movesLeft();
	}
}


//	Drawing the "+" to represent a king piece
function kingPiece(element){
	if(element.getAttribute("moveback") == undefined){
		element.setAttribute("moveback", "true");
		var ctx = element.getContext("2d");
		ctx.strokeStyle = "white";
		ctx.lineWidth=2;

		ctx.stroke();
		ctx.moveTo(35, 25);
		ctx.lineTo(15, 25);

		ctx.moveTo(25, 35);
		ctx.lineTo(25, 15);

		ctx.stroke();					
	}
}

function computerMove(response){
	var moveit = JSON.parse(response);
	if(moveit["state"] == "done" && moveit["positonold"] == undefined){
		freezeBoard(true);
		document.getElementById("status").innerHTML = "Game is done";
	}else{
		var oldcodinates = moveit["positonold"];
		var newcodinates = moveit["positonnew"];
		
		if(Math.abs(newcodinates[0] - oldcodinates[0]) == 2){
			/*
				Remove the piece that is getting jumped over
			*/
			var x = newcodinates[0]-oldcodinates[0];
			var y = newcodinates[1]-oldcodinates[1];

			var node = getJumptedPiece(newcodinates, x, y);
			node.removeChild(node.firstChild);
			movesLeft();
		}

		var nodeName = oldcodinates[0] + "-" + oldcodinates[1];
		var newTile = newcodinates[0] + "-" + newcodinates[1];
		
		//	Move the piece out of the old tile
		var node = document.getElementsByName(nodeName)[0];
		var boardSize = parseInt(document.getElementById("board").getAttribute("size"));
		if(newcodinates[1] == (boardSize-1)){
			kingPiece(node.children[0]);
		}
		document.getElementsByName(newTile)[0].append(node.children[0]);
			
		//	verifying that the game is not done
		if(moveit["state"] == "done"){
			freezeBoard(true);
			document.getElementById("status").innerHTML = "Game is done";
		}else{
			freezeBoard(false);
			document.getElementById("status").innerHTML = "It's your turn";
		}
		activPiece = undefined;	
	}
}


function gotoTile(tile){
	var validtile = Object.values(activeTiles).indexOf(tile.getAttribute("name"));
	if(validtile == -1){
		return 0;
	}
	document.getElementById("status").innerHTML = "Agent is thinking...";		
	//	Check if the move involves a jump
	checkIfJump(tile);
	//	Deactivate the tiles that were active 
	deactivateTiles();
	//	Move the piece that was selected to the new tile that was clicked
	tile.appendChild(activPiece);
	//	Make the piece a king piece if it has moved to the opposite side
	if(parseInt(tile.getAttribute("y")) == 0)
		kingPiece(activPiece)
	//	Disable the ability to move the pieces while computer is thinking
	freezeBoard(true);
	fetch('/boardmove', {
		method: 'POST',
		body: JSON.stringify({
			from: [activPiece.getAttribute("x"), activPiece.getAttribute("y")],
			to:[tile.getAttribute("x"), tile.getAttribute("y")]
		}),
		headers:{
			'Content-Type': 'application/json'
		}
	}).then(function(response) {
		return response.text();
	}).then(function(response) {
		//	Update coordinates
		activPiece.setAttribute("x", tile.getAttribute("x"));
		activPiece.setAttribute("y", tile.getAttribute("y"));
		computerMove(response);
	});	
}


function createPlayer(x, y, bricktype){
	var piece = document.createElement("canvas");
	piece.setAttribute("height" , "50");
	piece.setAttribute("width" , "50");
	piece.setAttribute("black", (bricktype == 0).toString());

	piece.addEventListener("click", function(){ 
		if(isBoardFrozen())
			getPlayableTiles(this);
	});
	piece.setAttribute("x", x);
	piece.setAttribute("y", y);

	//	Draw the circle representing the piece
	var ctx = piece.getContext("2d");
	ctx.beginPath();
	ctx.arc(25, 25, 23, 0, 2 * Math.PI);
	ctx.fillStyle = ((bricktype == 1) ? 'red' : '');
	ctx.fill();
	ctx.stroke();

	return piece;
}


function createTile(x, y, bricktype){
	var boardPiece = document.createElement("div");
	if(bricktype != undefined){
		boardPiece.appendChild(createPlayer(x, y, bricktype));						
	}		
	boardPiece.setAttribute("name", (x + "-" + y));
	boardPiece.setAttribute("id", "tile");			
	boardPiece.setAttribute("x", x);
	boardPiece.setAttribute("y", y);
	boardPiece.addEventListener("click", function(){ 
		if(isBoardFrozen())
			gotoTile(this);			
	});
	return boardPiece;
}

function createBoard(){
	fetch('/reset', {
		method: 'POST',
	}).then(function(response) {
		return response.text();
	}).then(function(response) {
		/*
			the json response contains coordinates of the black and red pieces.
		*/
		var responseJson = JSON.parse(response);
		var players = 	[	
							responseJson["playerRed"].concat(responseJson["playerBlack"]),
							responseJson["playerRed"],
							responseJson["playerBlack"]
						];
		var boardSize = responseJson["boardSize"];			

		document.getElementById("board").setAttribute("size", boardSize);
		//	Generate new row
		for(var y = 0; y < boardSize; y++){
			var rowBoard = document.createElement("div");
			rowBoard.setAttribute("id", "boardRow");
			//	Generate new column
			for(var x = 0; x < boardSize; x++){
				var containBrick = (players[0].indexOf(x + "-" + y) >= 0);
				var getBrick = undefined;
				if(containBrick){
					//	0	=	black
					//	1	=	red
					getBrick = (players[1].indexOf(x + "-" + y)) >= 0 ? 0 : 1;
				}					
				rowBoard.appendChild(createTile(x, y, getBrick));
			}
			document.getElementById("board").appendChild(rowBoard);
		}
	});
}

window.onload = function(){
	createBoard();
};	

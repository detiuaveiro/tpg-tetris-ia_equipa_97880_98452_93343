from collections import Counter

from shape import S
import math
import heapq

import asyncio
import getpass
import json
import os
import websockets

_bottom : list
grid : list
_height : int

rot_x = {}  # the leftmost x for each rotation of a given piece
_moves = {} # a cache of previously made command sequences

type_len = {
    "i":2,
    "o":1,
    "s":2,
    "z":2,
    "j":4,
    "l":4,
    "t":4
} # the number of rotations each piece has

piece_rotations = {} # These are calculated once game starts

class Jogada():
    def __init__(self, score, positions, gamestate, high_points, rotation) -> None:
        self.score = score
        self.positions = positions
        self.gamestate = gamestate
        self.high_points = high_points
        self.rotation = rotation

    def result(self):
        return [self.score, self.positions, self.rotation]

    def __str__(self) -> str:
        return str(self.rotation) + str(self.positions) + " Score:" + str(self.score)

#
# source for heuristics: https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
#
def validate_move(gamestate, lines, high_points):
    """Internal point system: attributes a number of points to a given move according to four parameters:
            - area: tells us how "high" a grid is (we want to minimize this value)
            - lines: the number of complete lines in a grid (we want to maximize this value)
            - holes: empty spaces such that there is at least one tile in the same column above them (we want to minimize this value)
            - bumpiness: the presence of deep "wells" in our grid (we want to minimize this value)
    """

    a = -0.510066   # area
    b = 0.760666    # lines
    c = -0.35663    # holes
    d = -0.184483   # bumpiness

    bumpiness = 0
    area = _height - high_points[-1]
    for i in range(len(high_points)-1):
        bumpiness += abs(high_points[i] - high_points[i+1]) 
        area += _height - high_points[i]

    holes = (area - (len(gamestate) - (len(_bottom)-2)))
    points = a*area + b*lines + c*holes + d*bumpiness
    return points 

def valid(piece, gamestate):
    """Checks if a piece can be in a given position 
    (doesn't overlap with any other piece already in the game)."""

    return not any(
        [piece_part in grid for piece_part in piece]
    ) and not any(
        [piece_part in gamestate for piece_part in piece]
    )


def calculate_move(highpoints, piece, column, floor_piece):
    """Calculates the possible move at a certain column.
        - Returns the move and line where the piece was placed
    """

    pivot = [0, _height+1]
    coords = []
    # Get the first column that intersects the piece
    for fp in floor_piece:
        if highpoints[column + fp[0] - 1] - fp[1] < pivot[1]:
            pivot = [fp[0], highpoints[column + fp[0] - 1] - fp[1]]
            coords = [fp[0], highpoints[column + fp[0] - 1]]

    # Calculate the piece location based on y of the column
    offset = max([y[1] for y in piece if y[0] == pivot[0]])
    move = [[p[0] + column, coords[1] - 1 + p[1] - offset] for p in piece ]
    return move, coords[1]

def getHighPoints(gamestate):
    """Returns an array containing the highest point (block) in each column."""

    highpoints = [_height] * (len(_bottom) - 2)
    for block in gamestate:
        highpoints[ block[0]-1 ] = block[1] if block[1] < highpoints[ block[0]-1 ] else highpoints[ block[0]-1 ]
    return highpoints


def what_is_this_pokemon(piece):
    """Identifies the type of piece given as input."""

    piece_code=[(piece[0][0]-piece[1][0], piece[0][1]-piece[1][1]),
                ((piece[2][0]-piece[3][0], piece[2][1]-piece[3][1]))]           # Essentially a hash for the piece
    if piece_code[0]==(-1,0):
        if piece_code[1]==(0,-1):
            return "j"
        if piece_code[1]==(-1,0):
            if (piece[0][0]-piece[3][0],piece[0][1]-piece[3][1])==(-1,-1):
                return "o"
            else:
                return "i"
    if piece_code[0]==(0,-1):
        if piece_code[1]==(-1,0):
            return "l"
        if piece_code[1]==(0,-1):
            return "s"
        if piece_code[1]==(1,-1):
            return "t"
    if piece_code[0]==(1,-1):
        return "z"


def clear_rows(gamestate, yy, offset):
    """Clears complete rows in the game.
            - Returns the new gamestate and the number of lines cleared
    """

    gamestate_copy = gamestate.copy()
    lines = 0
    
    # Get only the counter for the lines where the piece was placed on
    counter = Counter(y for _, y in gamestate_copy if y - offset in yy).most_common()
    counter.sort()                                                                  # sort to eliminate lines ordered by Y value
    for item, count in counter:
        if count == len(_bottom)-2 and item != _height:
            gamestate_copy = [(x, y) for (x, y) in gamestate_copy if y != item]     # remove row
            gamestate_copy = [
                (x, y + 1) if y < item else (x, y) for (x, y) in gamestate_copy
            ]                                                                       # drop blocks above
            lines += 1
    return gamestate_copy, lines

def tetris(piece_type, gamestate, high_points, look_ahead, pruning):
    """Main algorithm for playing the game."""
    
    if piece_type == None:
        return [0, None, 0]

    piece_r = piece_rotations[piece_type]   # all possible piece rotations
    score = -math.inf                       # piece score starts at lowest possible value
    cur_rotation = 0                        # loop iteration
    moves = []                              # sequence of moves for this piece  
    best = None                             # best play for this piece                                  
    
    for piece in piece_r:
        yy = []                             # (Relative coord) lines that the piece is in
        floor_piece = []                    # coordinates of the lowest blocks in the piece; for example, for a T piece:
                                            #   ### -> # #  |  #   ->  
        prev_x = -1                         #    #      #   | ###      ###
        for i in range(4):
            if piece[i][0] != prev_x:
                floor_piece.append(piece[i])
                prev_x = piece[i][0]
            if piece[i][1] not in yy:
                yy.append(piece[i][1])

        for i in range(1,len(_bottom) - len(floor_piece)):                          # Iterating over the possible piece placements
            move = calculate_move(high_points,piece,i,floor_piece)                  # Get possible move for current column 
            if move:                                                                # Get the needed values from this move and 
                new_gamestate = clear_rows(gamestate + move[0], yy, move[1])            # Get the gamestate after clearing lines and the number of lines cleared (if any)
                new_high_points = getHighPoints(new_gamestate[0])                           # Analyse the game board and get the high points in it
                new_score = validate_move(new_gamestate[0], new_gamestate[1], new_high_points)      # Calculate points for this play
                jog = Jogada(new_score, move[0], new_gamestate[0], new_high_points, cur_rotation)
                moves.append(jog)                                                   # Add move to list of possible plays

        cur_rotation += 1

    p = pruning if pruning < 6 else 6                               # Pruning used on the search tree (e.g. If pruning==6, only the best 6 possible plays will be
                                                                    # considered in calculating the best play for the next piece (if lookahead>0))
    best_n_plays = heapq.nlargest(p, moves, key=lambda x: x.score)  # Get the best plays from the list of possible plays according to the set pruning value

    for next_play in best_n_plays:                                                  # Iterate over best plays
        piece_type = what_is_this_pokemon(look_ahead[0]) if look_ahead else None    # Verify which piece is coming next 

        next_play.score += tetris(piece_type, next_play.gamestate,
                                  next_play.high_points, look_ahead[1:], pruning)[0] # Run again, if not done yet
        if next_play.score > score:                                                  # Check if new play gets a better score than the one we have already
            best = next_play
            score = next_play.score

    return best.result()

def get_command(objective, piece_type, rotation, move):
    """Get the corresponding command based on a given piece placement as the objective."""

    command = []
    if move not in _moves:                          # _moves is a cache of previously made command sequences
                                                    # if we don't have it already, we calculate the command sequence
        command.extend(["w"] * rotation)
        pivot = min([p[0] for p in objective])      # pivot = first piece block that will "touch" the gamestate
        min_x = rot_x[piece_type][rotation]         # the lefmost x of a given piece and rotation 

        translacao = pivot - min_x                  # we append the necessary moves to the command sequences according 
                                                    # to the piece movement
        if translacao < 0:
            command.extend("a"*(-1*translacao))
        elif translacao > 0:
            command.extend("d"*translacao)
        command.append("s")
        _moves[move] = command                      # store the move in the cache
    else:                                           # otherwise
        command = _moves[move]                      # we use a previous command sequence

    return command


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Main loop: agent playing the game."""

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        state = json.loads(
            await websocket.recv()
        )

        global _bottom
        global grid
        global _height

        x = state['dimensions'][0]
        _height = state['dimensions'][1]

        _bottom = [[i, _height] for i in range(x)]                              # bottom of the game board
        _lateral = [[0, i] for i in range(-5,_height)]                          # left border of the game board
        _lateral.extend([[len(_bottom) - 1, i] for i in range(-5,_height)])

        grid = _bottom + _lateral

        result = None   # result of the search for the best piece placement
        
        move = ""
        command = []            # sequence of commands to put the piece in its proper place
        piece_type = ""         # the piece type (given by a letter)
        num_rotations = 0       # how many times should the piece rotate to get its info
        
        while 1:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "piece" not in state:
                    break

                if not state.get("piece"):
                    result = None
                    command = []
                    move = ""
                    piece_type = ""
                else:
                    if not result and num_rotations == 0:

                        # get the high_points of the current board
                        high_points = getHighPoints(state["game"])

                        # find out what the current piece is 
                        piece_type = what_is_this_pokemon(state["piece"])
                        
                        # if piece hasn't been analyzed
                        if piece_type not in rot_x:
                            rot_x[piece_type] = []
                            piece_rotations[piece_type] = []
                            # Get the number of times needed to rotate the piece
                            num_rotations = type_len[piece_type]
                            # Send N rotations commands ("w")
                            command = ["w"]*(num_rotations)
                            continue

                        # get the rotations of the current piece
                        # add the floor border to calculate the Move 
                        current_gamestate = state["game"] + [[i,_height] for i in range(1, len(_bottom)-1)] 

                        lookahead = []
                        # Check if all pieces have already been stored to start looking ahead
                        if len(piece_rotations) == 7:
                            lookahead = state['next_pieces'][0:2]

                        result = tetris(piece_type, current_gamestate, high_points,lookahead, 2)

                        # Key of a move is for example: s:1:345
                        move = f"{piece_type}:{result[2]}:" + "".join([str(x[0]) for x in result[1]])

                    elif num_rotations == 0 and command == []:
                        command = get_command(objective=result[1], piece_type=piece_type, rotation=result[2], move=move)

                if num_rotations > 0:
                    # Get the pivots to calculate the relative position
                    min_x = min([x[0] for x in state["piece"]])
                    min_y = max([y[1] for y in state["piece"]])
                    rot_x[piece_type].append(min_x)
                    piece_rotations[piece_type].append([])
                    for p in state["piece"]:
                        piece_rotations[piece_type][-1].append([ p[0]- min_x, p[1] - min_y ])
                    # sort by x ascending and y descending
                    piece_rotations[piece_type][-1].sort(key=lambda x: [x[0], -x[1]])
                    num_rotations -= 1

                if command != []:
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": command[0]})
                    )  # send key command to server - you must implement this send in the AI age
                    command = command[1:]
                else:
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": ""})
                    )  # send key command to server - you must implement this send in the AI age
            except websockets.exceptions.ConnectionClosedOK:
                return

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))

# AVERAGE TIME: 0.0324
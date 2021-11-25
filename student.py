
from collections import Counter
import math
import time
#import logging

from shape import S

#logging.basicConfig(filename='playground.log', level=#logging.DEBUG)
_bottom = [[i, 30] for i in range(10)]  # bottom
_lateral = [[0, i] for i in range(-5,30)]  # left
_lateral.extend([[10 - 1, i] for i in range(-5,30)])

# grid = game boundaries
grid = _bottom + _lateral
#print(grid)

moves = {} # dicionario dos moves
rot_x = {} # dicionario com as Xs de cada rotação para cada peça

# Map with the rotations of each piece
piece_rotations = {
    "i": [
        [
            [0,0],[1,0],[2,0],[3,0]
        ],
        [
            [0,0],[0,-1],[0,-2],[0,-3]
        ]
    ],
    "o": [
        [[0,0],[1,0],[0,-1],[1,-1]]
    ],
    "s": [
        [
            [0,0],[0,-1],[-1,-1],[-1,-2]
        ],
        [
            [0,0],[1,0],[1,-1],[2,-1]
        ],
    ],
    "z": [
        [
            [0,0],[0,-1],[1,-1],[1,-2]
        ],
        [
            [0,0],[1,0],[1,1],[2,1]
        ],
    ],
    "l": [
        [
            [0,0],[1,0],[0,-1],[0,-2]
        ],
        [
            [0,0],[0,-1],[1,-1],[2,-1]
        ],
        [
            [0,0],[0,-1],[0,-2],[-1,-2]
        ],
        [
            [0,0],[1,0],[2,0],[2,-1]
        ],
    ],
    "j": [
        [                                        
            [0,0],[0,-1],[0,-2],[1,-2]
        ],
        [
            [0,0],[0,-1],[-1,-1],[-2,-1]
        ],                                     
        [
            [0,0],[1,0],[1,-1],[1,-2]
        ],
        [
            [0,0],[1,0],[2,0],[0,-1]            
        ],  
    ],
    "t": [
        [
            [0,0],[0,-1],[0,-2],[1,-1]
        ],
        [
            [0,0],[1,0],[2,0],[1,1]
        ],
        [
            [0,0],[0,-1],[0,-2],[-1,-1]
        ],
        [
            [0,0],[1,0],[2,0],[1,-1]
        ]
    ]
}

# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
"""
OLD validate_move
# Rank the move based on different criteria
def validate_move(gamestate, piece, high_points):
    
    
    allBlocks = gamestate + piece # blocks of all already set pieces + blocks of new piece (all blocks in board)
    #print("ALL BLOCKS: ", allBlocks)
    x_coords = []
    y_coords = []
    for block in piece:
        if block[0] not in x_coords:
            x_coords.append(block[0])
        if block[1] not in y_coords:
            y_coords.append(block[1])

    points = 0 # score of a given piece placement

    ### ------ ENCOURAGE COMPLETING LINES ------ 
    lines = 0 # number of lines completed with a given piece placement
    piece_min_height = min([p[1] for p in piece])
    counter = [y for _, y in allBlocks if y in y_coords ]

    # checking if any lines are complete
    for item, count in Counter(counter).most_common():
        if count == 8 and item != 30:
            lines += 1 # if so, increment "lines"
        elif count == 7:
            # Motivate the piece to form holes of more than one block to wrack more points
            if piece_min_height > 20:
                points += 3

    # the point score increments exponentially according to the number of lines completed at once by a piece placement
    points += (lines ** 2)

    #logging.debug(f"FROM LINES: {(lines ** 2)} / {points - (lines ** 2)}")
    before = points
    ### ------ DISCOURAGE HOLES ------
    for x in x_coords:
        column = [high_points[x -1]] + [p[1] for p in piece if p[0] == x]
        column.sort()
        for i in range(len(column)-1):
            if column[i+1] - column[i] > 1:
                points-= (column[i+1] - column[i]) * 2

    #logging.debug(f"FROM HOLES: {points - before}")
    before = points
    ### ------ ENCOURAGE FLAT PLAYING STYLE ------

    top_of_the_piece = min(y_coords)
    points -= (30 - top_of_the_piece)

    ##logging.debug(f"TMP2: {tmp2}, {round(tmp2/10)}")

    #logging.debug(f"FROM HEIGHT: {points - before}")
    #logging.debug(f"TOTOAL: {points}")
    return points
"""  

def validate_move(piece, high_points, lines, lines_cleared):

    points = 0

    piece_columns = []
    piece_rows = []
    for i in piece:
        if i[0] not in piece_columns and i[1] not in lines_cleared:
            piece_columns.append(i[0])
        if i[1] not in piece_rows:
            piece_rows.append(i[1])

    points += lines**2
    bumpiness = 0
    points -= bumpiness//2
    
    for xx in piece_columns:
        t = [high_points[xx-1]] + [p[1] for p in piece if p[0] == xx]
        t.sort()

        for i in range(len(t)-1):
            if t[i+1] - t[i] > 1:
                points -= (t[i+1] - t[i]) * 2 -1 if (t[i+1] - t[i]) < 6 else (t[i+1] - t[i]) - 2
    tmp2 = min(piece_rows)
    if tmp2 + lines < 10:
        points -= (30 - tmp2 + lines) * 20
    elif tmp2 + lines < 20:
        points -= round((30 - tmp2 + lines) * 2)
    else:
        points -= round((30 - tmp2 + lines) * 1.50)
    return points

# Check if a piece placement is valid (doesn't overlap with anything)
def valid(placement, gamestate):
    # check if the piece placement doesn't overlap with the game boundaries
    return not any(
        [block in grid for block in placement]
    # check if the piece placement doesn't overlap with any already set pieces
    ) and not any(
        [block in gamestate for block in placement]
    )

# Calculate the possible move at a certain column
def calculate_move(gamestate, piece, column):

    ### GAMESTATE: list of lists
    ### [ [columnNumber, height], [columnNumber, height], [columnNumber, height], ...  ], for the 8 columns
    ### if column 5 has 3 stacked blocks, all [5,30], [5,29] and [5,28] (the used up blocks) will be in the list of lists
    ### this allows us to see when a full line is formed

    ### PIECE: list of 4 lists (each of the smaller lists is the position of one of the piece's blocks)
    ### the piece is already in one of its positions, see the big map on top with the rotations of each type of piece

    pivot = 30
    for block in gamestate:
        if block[0] == column and block[1] < pivot:
            pivot = block[1]
        
    # we're gonna try to find a piece placement now. a piece is 4 blocks tall maximum
    # we try to place it as it is. if it's not possible (because it's overlapping with pieces already in the game), we
    # adjust it one block up (because if it overlaps, it overlaps at the bottom)
    # range(1,5) = [1,2,3,4], four possible adjustments (bc of the max piece height)
    for adjust in range(1,5): 
        # block = block in piece (it's a list with 2 coordinates for that block)
        # block[0]=x, block[1]=y
        #               x + column       y + pivot - n
        # the placement is given in absolute coords in the game viewer
        placement = [ [ block[0]+column, block[1]+pivot-adjust ] for block in piece ]

        if valid(placement,gamestate): # check if the new piece doesn't overlap with already set game pieces for this placement
            return placement

def getHighPoints(state, game):
    tmp = state.copy()
    for block in game:
        tmp[ block[0]-1 ] = block[1] if block[1] < tmp[ block[0]-1 ] else tmp[ block[0]-1 ]
    return tmp

def discover_i(piece):
    if piece != None:
        x = piece[0][0]
        y = piece[0][1]
        b = [True,True]
        for coor in piece:
            if coor[0] != x:
                b[0] = False
            if coor[1] != y:
                b[1] = False
        return b  
    return [False,False]

def what_is_this_pokemon(piece):
    """I'm sure this can be improved. Base 3 maybe?"""
    is_i=discover_i(piece)
    if is_i[0] or is_i[1]:
        return "i"
    #print(discover_i(piece))
    piece_code=[(piece[0][0]-piece[1][0], piece[0][1]-piece[1][1]),((piece[2][0]-piece[3][0], piece[2][1]-piece[3][1]))]
    #print("current piece has a code of: "+str(piece_code))
    if piece_code[0]==(-1,0):
        if piece_code[1]==(0,-1):
            return "j"
        if piece_code[1]==(-1,0):
            return "o"
    if piece_code[0]==(0,-1):
        if piece_code[1]==(-1,0):
            return "l"
        if piece_code[1]==(0,-1):
            return "s"
        if piece_code[1]==(1,-1):
            return "t"
    if piece_code[0]==(1,-1):
        return "z"

#
# Get the up to date gamestate and count the lines cleared
#
def clear_rows(gamestate):
    tmp = gamestate.copy()
    lines = 0
    counter = Counter(y for _, y in tmp).most_common()
    counter.sort() # sort to eliminate lines ordered by Y value
    lines_cleared = []
    for item, count in counter:
        if count == 8 and item != 30:
            tmp = [(x, y) for (x, y) in tmp if y != item]  # remove row
            tmp = [
                (x, y + 1) if y < item else (x, y) for (x, y) in tmp
            ]  # drop blocks above
            lines += 1
            lines_cleared.append(count)
    return tmp, lines, lines_cleared

"""
OLD tetris
# get the best possible move of a given piece
def tetris(type, gamestate, high_points, look_ahead, tabs):
    ### PIECE_R: piece rotations
    ### in order to assess which is the best move for a new piece, we need to take into account all of the possible
    ### placements of said piece, in all its possible positions (rotations)
    ### if we're trying to place a T piece (for example), piece_r will be the list of lists containing all of T's
    ### possible rotations (this information is taken directly from the big rotations map on top of the code)
    piece_r = piece_rotations[type]
    highestScore = None # score of the highest scoring position for this piece
    rotationIdx = 0 # index of the position in piece_r (tells us which position we're talking about)
    bestPosition = [] # information about the highest scoring position, format = [<score>,<positionIdx>,<piece placement>]
    for piece in piece_r: # for each rotation of the piece
        for column in range(1,9): # for each column
            ##logging.debug(f"Column: {column}")
            piece_score = calculate_move(gamestate, piece, column, high_points) # piece_score = (<score>,<piece placement>)
            ##logging.debug(f"Move: {piece_score}")

            # ------ store the information of the highest scoring position in bestPosition ------
            if highestScore is None and piece_score is not None:
                highestScore = piece_score[0]
                bestPosition = [piece_score[1], rotationIdx, piece_score[0]]
            elif piece_score is not None and highestScore < piece_score[0]:
                highestScore = piece_score[0]
                bestPosition = [piece_score[1], rotationIdx, piece_score[0]]
            # -----------------------------------------------------------------------------------
        rotationIdx += 1
    #logging.debug(f"Best Result: {bestPosition}")
    return bestPosition
"""
def tetris(type, gamestate, high_points, look_ahead, tabs):
    piece_r = piece_rotations[type]
    score = -math.inf
    curr_rotation = 0
    objective = []
    for piece in piece_r:
        for i in range(1,9):

            move = calculate_move(gamestate,piece,i)

            if move is not None:
                if not look_ahead:
                    tmp1 = clear_rows(gamestate + move)
                    tmp2 = getHighPoints(high_points,tmp1[0])
                    tmp = validate_move(move,high_points,tmp1[1],tmp1[2])

                    if tmp > score:
                        score = tmp
                        objective = [tmp, move, curr_rotation, None]
                else:
                    tmp1 = clear_rows(gamestate + move)
                    tmp2 = getHighPoints(high_points,tmp1[0])
                    tmp_score = validate_move(move,high_points, tmp1[1],tmp1[2])
                    
                    tmp = tetris(what_is_this_pokemon(look_ahead[0]), tmp1[0], tmp2, look_ahead[1:], tabs + 2)
                    if tmp:
                        tmp_score += tmp[0]

                    if tmp and tmp_score > score:
                        score = tmp_score
                        objective = [tmp_score, move, curr_rotation, tmp[1]]        
        curr_rotation += 1
    return objective


def get_command(objective, piece_type, rotation, move):
    command = []
    if move not in moves:
        command.extend(["w"] * rotation)
        pivot = min([p[0] for p in objective])
        piece = rot_x[piece_type][rotation]
        translacao = pivot - piece
        if translacao < 0:
            command.extend("a"*(-1*translacao))
        elif translacao > 0:
            command.extend("d"*translacao)
        command.append("s")
        moves[move] = command
    else:
        command = moves[move]
    return command
        


# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

import asyncio
import getpass
import json
import os

import websockets

# Next 4 lines are not needed for AI agents, please remove them from your code!

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        n = 0
        obj = None
        times_to_rotate = 0
        move = ""
        command = []
        piece_type = ""
        final_score = 0
        flg = False
        count = 0
        tot_time = 0
        while 1:
            high_points = [30 for i in range(8)] # The height of each column
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "score" in state:
                    final_score = state["score"]

                # Reset vars
                if not state["piece"]:
                    obj = None
                    command = []
                    move = ""
                    piece_type = ""
                    flg = True

                else:
                    if not obj:
                        # get the high_points of the current board
                        if n != 0:
                            high_points = getHighPoints(high_points, state["game"])
                        n += 1
                        # find out what the current piece is 
                        piece_type = what_is_this_pokemon(state["piece"])
                        if piece_type not in rot_x:
                            rot_x[piece_type] = []
                            times_to_rotate = len(piece_rotations[piece_type])
                            command = ["w"]*(times_to_rotate)
                        
                        # add the floor border to calculate HOLES based on it
                        tmp = state["game"] + [[i,30] for i in range(1,9)] 
                        tic = time.perf_counter()
                        obj = tetris(piece_type, tmp, high_points,state['next_pieces'][0:1], 0)
                        toc = time.perf_counter()
                        count += 1
                        tot_time += (toc - tic)
                        move = f"{obj[2]}" + "".join([str(x[0]) for x in obj[1]])
                        #print("TYPE:",piece_type)
                        #print("OOOBJ", obj)
                    elif times_to_rotate == 0 and command == [] and flg:
                        command = get_command(objective=obj[1], piece_type=piece_type, rotation=obj[2], move=move)
                        flg = False

                if times_to_rotate > 0:
                    rot_x[piece_type].append(min([x[0] for x in state["piece"]]))
                    times_to_rotate -= 1   

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
                print(final_score)
                print("Server has cleanly disconnected us")
                print(f"AVERAGE TIME: {tot_time/count:0.4f}")
                return

            # Next line is not needed for AI agent


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))

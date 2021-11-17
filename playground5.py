
from collections import Counter

from shape import S
import logging
import math
import heapq

#logging.basicConfig(filename='playground.log', level=logging.DEBUG)
_bottom = [[i, 30] for i in range(10)]  # bottom
_lateral = [[0, i] for i in range(-5,30)]  # left
_lateral.extend([[10 - 1, i] for i in range(-5,30)])


grid = _bottom + _lateral
####print(grid)

rot_x = {}
moves = {}


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
        [[0,0],[0,-1],[1,0],[1,-1]]
    ],
    "s": [
        [
            [0,-1],[0,-2],[1,0],[1,-1]
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
            [0,-1],[1,0],[1,-1],[2,0]
        ],
    ],
    "l": [
        [
            [0,0],[0,-1],[0,-2],[1,0]
        ],
        [
            [0,0],[0,-1],[1,-1],[2,-1]
        ],
        [
            [0,-2],[1,0],[1,-1],[1,-2]
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
            [0,-1],[1,-1],[2,0],[2,-1]
        ],                                     
        [
            [0,0],[1,0],[1,-1],[1,-2]
        ],
        [
            [0,0],[0,-1],[1,0],[2,0]           
        ],  
    ],
    "t": [
        [
            [0,0],[0,-1],[0,-2],[1,-1]
        ],
        [
            [0,-1],[1,0],[1,-1],[2,-1]
        ],
        [
            [0,-1],[1,0],[1,-1],[1,-2]
        ],
        [
            [0,0],[1,0],[1,-1],[2,0]
        ]
    ]
}

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
        return str(self.rotation) + str(self.positions)



def validate_move(gamestate, piece, high_points, lines, new_high_points, tabs):     
    a = -0.510066
    b = 0.760666
    c = -0.35663
    d = -0.184483

    bumpiness = 0
    area = 30 - new_high_points[-1]
    for i in range(len(new_high_points)-1):
        bumpiness += abs(new_high_points[i] - new_high_points[i+1]) 
        area += 30 - new_high_points[i]

    holes = (area - (len(gamestate) - 8))

    points = a*area + b*lines + c*holes + d*bumpiness

    return points 

# Check if a piece can be there
def valid(piece, gamestate):
        return not any(
            [piece_part in grid for piece_part in piece]
        ) and not any(
            [piece_part in gamestate for piece_part in piece]
        )


# Calculate the possible move at a certain column
def calculate_move(gamestate, piece, column, xx, yy):
    ####print(column)
    ##print("HP", gamestate)
    pivot = 31
    c = 0
    tmp = []
    for x in xx:
        if gamestate[column + x - 1] - yy[x] < pivot:
            pivot = gamestate[column + x - 1] - yy[x]
            c = x
            tmp = [x,gamestate[column + x - 1]]

    #for block in range(1,9):
    #    if block - column in xx:
    #        ####print("AA",block, block[1] - yy[block[0] - column])
    #        if gamestate[block-1] - yy[block - column] < pivot:
    #            ####print("BB", block)
    #            pivot = gamestate[block-1] - yy[block - column]
    #            c = block - column
    #            tmp = [block,gamestate[block-1]]
    ###print("PIVOT", c, pivot)
    ###print("PIECE", piece)
    offset = max([y[1] for y in piece if y[0] == c])
    ####print("OFFSET", offset)
    bb = [[p[0] + column, tmp[1] - 1 + p[1] - offset] for p in piece ]
    return bb, tmp[1]

def getHighPointsFast(highpoints, piece, lines):
    print("HP",highpoints)
    tmp = [p-lines for p in highpoints]
    for p in piece:
        tmp[p[0] - 1] = p[1]-lines if p[1]-lines < tmp[p[0] - 1] else tmp[p[0] - 1]
    print("TMP", tmp)
    return tmp

def getHighPoints(gamestate):
    tmp = [30, 30, 30, 30, 30, 30, 30, 30]
    for block in gamestate:
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
    ####print(discover_i(piece))
    piece_code=[(piece[0][0]-piece[1][0], piece[0][1]-piece[1][1]),((piece[2][0]-piece[3][0], piece[2][1]-piece[3][1]))]
    ####print("current piece has a code of: "+str(piece_code))
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

def clear_rows(gamestate, yy, pivot):
    tmp = gamestate.copy()
    lines = 0
    counter = Counter(y for _, y in tmp if y - pivot in yy).most_common()
    counter.sort() # sort to eliminate lines ordered by Y value
    for item, count in counter:
        if count == 8 and item != 30:
            tmp = [(x, y) for (x, y) in tmp if y != item]  # remove row
            tmp = [
                (x, y + 1) if y < item else (x, y) for (x, y) in tmp
            ]  # drop blocks above
            lines += 1
    return tmp, lines


# get the best possible move of a given piece
def tetris(type, gamestate, high_points, look_ahead, tabs):
    #####print((tabs)*"\t"  + "TYPE: " + type)
    #####print((tabs)*"\t"  + f"GS: {gamestate}")
    piece_r = piece_rotations[type]
    best_score = -math.inf
    score = -math.inf
    n = 0
    a = []
    moves = []
    for piece in piece_r:
        floor_x = []
        floor_y = []
        prev_x = -1
        yy = []
        for i in range(4):
            if piece[i][0] != prev_x:
                floor_x.append(piece[i][0])
                floor_y.append(piece[i][1])
                prev_x = piece[i][0]
            if piece[i][1] not in yy:
                yy.append(piece[i][y])
        for i in range(1,9 - len(floor_x) + 1):
            ##print(((tabs)*"\t" +str(n)+ " " + "TYPE: " + type + " " + str(i)))
            s = calculate_move(high_points,piece,i,floor_x, floor_y)

            ##print((tabs)*"\t" + f"Move: {s}")
            if s is not None:
                ######print(tabs*"\t" + f"OLD HP: {high_points}")
                tmp1 = clear_rows(gamestate + s)
                #tmp2 = getHighPointsFast(high_points, s, tmp1[1])
                tmp2 = getHighPoints(tmp1[0])
                ######print(tabs*"\t" + f"NEW HP: {tmp2}")
                ######print(tabs*"\t" + f"NEW GS: {tmp1}")
                if not look_ahead:


                    tmp = validate_move(tmp1[0],s,high_points,tmp1[1],tmp2, tabs)

                    ######print("SCORE",tmp)
                    ######print("PIECE", piece)
                    ######print("GS:", gamestate)
                    if tmp > score:
                        score = tmp
                        a = [tmp, s, n, None]
                    ##print(tabs*"\t" + f"SCORE: {tmp}") 
                else:
                    tmp_score = validate_move(tmp1[0],s,high_points, tmp1[1],tmp1[2], tmp2, tabs)
                    ####print(tmp2)
                    tmp = tetris(what_is_this_pokemon(look_ahead[0]), tmp1[0], tmp2, look_ahead[1:], tabs + 2)
                    if tmp:
                        tmp_score += tmp[0]
                        #print(tabs*"\t" + f"SCORE: {tmp_score}")
                    ######print("TET", tmp)
                    ######print("SCORE: ", type, i, tmp_score)
                    if tmp and tmp_score > score:
                        score = tmp_score
                        a = [tmp_score, s, n, tmp[1]]                            
        n += 1
    #print((tabs)*"\t" + f"Best Result for {type}: {a}")
    return a



def tetris2(type, gamestate, high_points, look_ahead, tabs, pruning):
    if type == None:
        return [0, None, 0]
    piece_r = piece_rotations[type]
    score = -math.inf
    n = 0
    moves = []
    best = None
    #second_best = None
    #print("T",type)
    floor_x = []
    yy = []
    for piece in piece_r:
        floor_x = []
        floor_y = []
        prev_x = -1
        for i in range(4):
            if piece[i][0] != prev_x:
                floor_x.append(piece[i][0])
                floor_y.append(piece[i][1])
                prev_x = piece[i][0]
            if piece[i][1] not in yy:
                yy.append(piece[i][1])
        for i in range(1,9 - len(floor_x) + 1):
            s = calculate_move(high_points,piece,i,floor_x, floor_y)
            if s is not None:
                tmp1 = clear_rows(gamestate + s[0], yy, s[1])
                tmp2 = getHighPoints(tmp1[0])
                tmp = validate_move(tmp1[0],s,high_points,tmp1[1],tmp2, tabs)
                jog = Jogada(tmp,s[0],tmp1[0],tmp2,n)
                #if best is None:
                #    best = jog
                #elif jog.score > best.score:
                #    second_best = best
                #    best = jog
                #elif second_best is None:
                #    second_best = jog
                #elif jog.score > second_best.score:
                #    second_best = jog

                moves.append(jog)
        n += 1
    p = pruning if pruning < 6 else 6
    tmp4 = heapq.nlargest(p, moves, key=lambda x: x.score)
    for i in range(p):
        next = tmp4[i]
        #print(next)
        t = what_is_this_pokemon(look_ahead[0]) if look_ahead else None
        #print("NEXT", t, look_ahead)
        next.score += tetris2(t, next.gamestate, next.high_points, look_ahead[1:], tabs + 2, pruning)[0]
        if next.score > score:
            best = next
            score = next.score
    #t = what_is_this_pokemon(look_ahead[0]) if look_ahead else None
    #best.score += tetris2(t, best.gamestate, best.high_points, look_ahead[1:], tabs + 2, pruning)[0]
    #second_best.score += tetris2(t, second_best.gamestate, second_best.high_points, look_ahead[1:], tabs + 2, pruning)[0]

    return best.result()
    #return best.result() if best.score > second_best.score else second_best.result()



def get_command(objective, piece_type, rotation, move):
    command = []
    if move not in moves:
        command.extend(["w"] * rotation)
        pivot = min([p[0] for p in objective])
        # pivot = 7
        piece = rot_x[piece_type][rotation]
        # piece = 3
        ###print("ROT_X",rot_x[piece_type])
        translacao = pivot - piece
        if translacao < 0:
            command.extend("a"*(-1*translacao))
        elif translacao > 0:
            command.extend("d"*translacao)
        command.append("s")
        moves[move] = command
    else:
        command = moves[move]
    ###print("C:",command,move)
    return command


import asyncio
import getpass
import json
import os
import time

import websockets

# Next 4 lines are not needed for AI agents, please remove them from your code!

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        n = 0
        #high_points = [30 for i in range(8)] # The height of each column
        obj = None
        flg = True
        
        move = ""
        command = []
        rot = []
        prev = [30 for i in range(4)]
        final_score = 0
        sum = 0
        count = 0
        sum1 = 0
        count1 = 0
        start_pos = []
        p_t = ""
        piece_type = ""
        c = 1
        while 1:
            high_points = [30 for i in range(8)] # The height of each column
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                if "score" in state:
                    final_score = state["score"]
                key = ""
                
                if not state["piece"]:
                    obj = None
                    command = []
                    move = ""
                    flg = True
                    piece_type = ""
                else:
                    if not obj:
                        #print(c)
                        #print(state)
                        c += 1
                        # get the high_points of the current board
                        if n != 0:  
                            high_points = getHighPoints(state["game"])
                            ####print("HHHHHHHHHHHHHHHHHHHHHHHHH", high_points)
                        n += 1
                        # find out what the current piece is 
                        piece_type = what_is_this_pokemon(state["piece"])
                        if piece_type not in rot_x:
                            p_t = piece_type
                            rot_x[p_t] = []
                            b = len(piece_rotations[p_t])
                            command = ["w"]*(b)

                       
                        #start_pos = state["piece"]
                        # get the rotations of the current piece
                        # add the floor border to calculate HOLES based on it
                        tmp = state["game"] + [[i,30] for i in range(1,9)] 
                        ###print(tmp)
                        #
                        #
                        #
                        tic = time.perf_counter()

                        obj = tetris2(piece_type, tmp, high_points,state['next_pieces'][0:2], 0, 2)
                        toc = time.perf_counter()
                        count += 1
                        sum += (toc - tic)
                        #print(f"Elapsed time {toc - tic:0.4f} seconds")
                        #print("TYPE:",piece_type)
                        #print("OOOBJ", obj)
                        move = f"{piece_type}{obj[2]}" + "".join([str(x[0]) for x in obj[1]])


                    elif b == 0 and command == [] and flg:
                        
                        tec = time.perf_counter()
                        count1 += 1
                        command = get_command(objective=obj[1], piece_type=piece_type, rotation=obj[2], move=move)
                        tac = time.perf_counter()
                        sum1 += (tac - tec)
                        flg = False
                        ####print(f"Elapsed Move time {tac - tec:0.8f} seconds")

                if b > 0:
                    rot_x[p_t].append(min([x[0] for x in state["piece"]]))
                    b -= 1

                if command != []:
                    ####print("COMMAND", command)
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": command[0]})
                    )  # send key command to server - you must implement this send in the AI age
                    command = command[1:]
                    ####print("COMMANDAFT", command)
                else:
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": ""})
                    )  # send key command to server - you must implement this send in the AI age
            except websockets.exceptions.ConnectionClosedOK:
                ####print("Server has cleanly disconnected us")
                print(final_score)
                print(f"AVERAGE TIME: {sum/count:0.4f}")
                ###print(f"AVERAGE MOVE TIME: {sum1/count1:0.8f}")
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
'''
The goal of this script is to prepare data and then use it to train a NN to evaluate chess positions
and then save it.

As training data i used a set of data that was created through one second evaluations (on one core)
of chess board states by stockfish (version from 2015), the strongest CPU chess engine in
the world (currently, 2023). The dataset needed for evaluation came from the website chess.com
and is stored in data.pgn. Here 50,000 "events" are listed, each corresponding to one game
of chess which ended either in a draw, checkmate or stalemate.
One chess game lasts 40 moves on average (80 positions), so around 4*10^6 board states build
our dataset.

Each boardstate of every game has one feature in this case, the evaluation of the
board state, which is centipawns (cp), where 100 cp = 1 pawn which is an arbritrary unit and
is > 0 if white has the advantage and < 0 if black is winning.

-----------------------------------------------------------------------------------------

Since the portable game notation filetype (pgn) has a lot of unecessary information, at first
I will filter it for the event (game played) and the moves.

Then follows feeding each individual game into my chess engine and extracting each of the boardstates.

After that Im merging the extracted data with the data from the corresponding evaluated positions in 
stockfish.csv, such that I have only boardstates with their corresponding evaluations in a file.

'''

import re
from chess_module import *
import json

def extract_moves(source_file, target_file):
    matches=[]
    # create a pattern for recognizing move counts, endgame results, + signs
    remove_patterns=re.compile(r"\d+\.|\d-\d|\d/\d-\d/\d|\+|x|#") # pawn promotions are left in (eg. '=Q')
    with open(source_file) as source:
        for line in source:
            line=line.strip()
            if not line or line.startswith("["): # ignore empty lines and lines which start with [
                continue
            else:
                if line.startswith("1. "): # detect new match
                    matches.append([])
                cleaned_line=re.sub(remove_patterns, "", line) # removing what matches patterns
                moves_string=cleaned_line.split()
                matches[-1].extend(moves_string)
    
    json_data=json.dumps(matches)
    
    with open(target_file, "w") as target:
        target.write(json_data)
    
def generate_board_states_board_rep(source_file, target_dir):
    boards=[]
    gamestate=chess_board()
    count=0
    with open(source_file, "r") as source:
        json_data=source.read()
        matches=json.loads(json_data)
        for match in matches:
            gamestate.reset_board()
            count+=1
            print("Generating board states of game number: ", count)
            for move in match:
                gamestate.make_move_UCI(move)
                gamestate.whites_turn = not gamestate.whites_turn
                rep=gamestate.convert_to_board_representation()
                boards.append(rep)
    
    # save boards into a file
    # since we use numpy arrays, we want to use the .npy format
    boards=np.array(boards)
    np.save(target_dir+"boards_board_representation.npy", boards)

def combine_evals_with_board_rep(eval_file, boards_rep_file, target_file):
    boards=np.load(boards_rep_file)
    
    with open(eval_file) as evals:
        for line in evals:
            if re.match(r"^\d", line):
                pass
            else:
                continue
    
'''
Extract the moves from the data and write them into a JSON file:
'''

# extract_moves("data/evaluated_positions/data.pgn", "data/evaluated_positions/extracted_moves.json")

'''
Generate board states from the extracted moves, and write them ordered into a numpy array:
'''

# generate_board_states_board_rep("data/evaluated_positions/extracted_moves.json", "data/evaluated_positions/")

'''
Now get board evaluations from stockfish.csv and pair them with corresponding board states to form our base dataset for the NN:
'''

combine_evals_with_board_rep("data/evaluated_positions/extracted_moves.json", "data/evaluated_positions/boards_board_representation.npy", "test")



# CODE FOR DEBUGGING STANDARDIZED MOVE READ-INS:
# gamestate=chess_board()
# gamestate.reset_board()
# while True:
    # print(gamestate)
    # next_move=input("next move in standard notation: ")
    # gamestate.make_move_UCI(next_move)
    # gamestate.whites_turn=not gamestate.whites_turn
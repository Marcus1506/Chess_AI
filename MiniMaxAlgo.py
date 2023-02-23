# these are the algorithms for calculating and evaluating future moves

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
import random

DEPTH=2
CHECKMATE_SCORE=1.
STALEMATE_SCORE=0.

DUMB_PIECE_SCORES={'p': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 4} # king value here only for neural network input
# the value of 4 is chosen, becaue in the later stages of the game the king becomes more and more powerful

def dumb_eval(gs): # a dumb way of evaluating positions on the chess board
    if gs.checkmate:
        if gs.whites_turn:
            return -CHECKMATE_SCORE*1000
        else:
            return CHECKMATE_SCORE*1000
    elif gs.stalemate:
        return STALEMATE_SCORE*1000
    
    score=0
    
    for row in gs.get_board():
        for piece in row:
            if piece:
                if piece.rep=="K":
                    continue
                elif piece.color=='w':
                    score+=DUMB_PIECE_SCORES[piece.rep]
                else:
                    score-=DUMB_PIECE_SCORES[piece.rep]
    print('dumb here')
    return score

def model_eval(gs, evaluator): # evaluating gamestate with neural network
    if gs.checkmate:
        if gs.whites_turn:
            return -CHECKMATE_SCORE
        else:
            return CHECKMATE_SCORE
    elif gs.stalemate:
        return STALEMATE_SCORE
    else: # get evaluated position from the evaluator
        # using model() since this is faster than predict for single evaluations
        return evaluator(gs.convert_to_board_representation().reshape(1,64), training=False)[0,0]
        

def find_good_move(gs, valid_moves, evaluator=None):
    global next_move
    next_move=None # since next_move is handled globally resetting before every use
    random.shuffle(valid_moves) # shuffling moves, also ordering in terms of likeability of good moves could be faster
    # mini_max_dumb_eval(gs, valid_moves, DEPTH)
    # nega_max_eval(gs, valid_moves, DEPTH, evaluator, 1 if gs.whites_turn else -1)
    nega_max_eval_with_pruning(gs, valid_moves, DEPTH, -CHECKMATE_SCORE, CHECKMATE_SCORE, evaluator, 1 if gs.whites_turn else -1)
    return next_move

def mini_max_dumb_eval(gs, valid_moves, depth):
    global next_move
    if depth==0 or gs.checkmate or gs.stalemate:
        return dumb_eval(gs)
    
    if gs.whites_turn:
        max_eval=-CHECKMATE_SCORE
        for move in valid_moves:
            gs.move_piece(move)
            next_moves=gs.get_valid_moves()
            eval=mini_max_dumb_eval(gs, next_moves, depth-1)
            if eval > max_eval:
                max_eval=eval
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
        return max_eval
    else:
        min_eval=CHECKMATE_SCORE
        for move in valid_moves:
            gs.move_piece(move)
            next_moves=gs.get_valid_moves()
            eval=mini_max_dumb_eval(gs, next_moves, depth-1)
            if eval < min_eval:
                min_eval=eval
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
        return min_eval

def mini_max_eval(gs, valid_moves, depth, evaluator):
    global next_move
    if depth==0 or gs.checkmate or gs.stalemate:
        return model_eval(gs, evaluator)
    
    if gs.whites_turn:
        max_eval=-CHECKMATE_SCORE
        for move in valid_moves:
            gs.move_piece(move)
            next_moves=gs.get_valid_moves()
            eval=mini_max_eval(gs, next_moves, depth-1, evaluator)
            if eval > max_eval:
                max_eval=eval
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
        return max_eval
    else:
        min_eval=CHECKMATE_SCORE
        for move in valid_moves:
            gs.move_piece(move)
            next_moves=gs.get_valid_moves()
            eval=mini_max_eval(gs, next_moves, depth-1, evaluator)
            if eval < min_eval:
                min_eval=eval
                if depth==DEPTH:
                    next_move=move
            gs.undo_move()
        return min_eval

def nega_max_eval(gs, valid_moves, depth, evaluator, turn_multiplier):
    global next_move
    if depth==0 or gs.checkmate or gs.stalemate:
        return turn_multiplier*model_eval(gs, evaluator)
    
    max_eval=-CHECKMATE_SCORE
    for move in valid_moves:
        gs.move_piece(move)
        next_moves=gs.get_valid_moves()
        eval=-nega_max_eval(gs, next_moves, depth-1, evaluator, -turn_multiplier)
        if eval > max_eval:
            max_eval=eval
            if depth==DEPTH:
                next_move=move
        gs.undo_move()
    return max_eval

def nega_max_eval_with_pruning(gs, valid_moves, depth, alpha, beta, evaluator, turn_multiplier):
    global next_move
    if depth==0 or gs.checkmate or gs.stalemate:
        return turn_multiplier*model_eval(gs, evaluator)
    
    # move ordering - could also implement here for better pruning performance
    
    max_eval=-CHECKMATE_SCORE
    for move in valid_moves:
        gs.move_piece(move)
        next_moves=gs.get_valid_moves()
        eval=-nega_max_eval_with_pruning(gs, next_moves, depth-1, -beta, -alpha, evaluator, -turn_multiplier)
        if eval > max_eval:
            max_eval=eval
            if depth==DEPTH:
                next_move=move
        gs.undo_move()
        if max_eval > alpha:
            alpha=max_eval
        if alpha >= beta: # early pruning, not evaluating other possibilities
            break
    return max_eval

# these are the algorithms for calculating and evaluating future moves

DEPTH=2
CHECKMATE_SCORE=1000
STALEMATE_SCORE=0

DUMB_PIECE_SCORES={'p': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9}

def dumb_eval(gs): # a dumb way of evaluating positions on the chess board
    if gs.checkmate:
        if gs.whites_turn:
            return -CHECKMATE_SCORE
        else:
            return CHECKMATE_SCORE
    elif gs.stalemate:
        return STALEMATE_SCORE
    
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
    return score

def find_good_move(gs, valid_moves):
    global next_move
    next_move=None # since next_move is handled globally resetting before every use
    mini_max_dumb_eval(gs, valid_moves, DEPTH)
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
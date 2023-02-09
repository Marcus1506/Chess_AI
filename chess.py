import numpy as np
import ast

# having the pieces in chess_board not directly labeled according to their IMAGE makes the __ini__ functions of the piece classes really messy
# maybe try to change that

# convention: white at the top

BOARD_DIM=8

class chess_board:
    def __init__(self, id=0, whites_turn=True): # give chess board ids to make multiple instances possible
        self.board=np.full((8, 8), None, dtype=object)
        self.id=id
        self.whites_turn=whites_turn # means white starts
        self.move_log=[]
        self.white_king_loc=[0,4]
        self.black_king_loc=[7,4]
    
    def place_piece(self, position, piece):
        self.board[position[0],position[1]]=piece
    
    def remove_piece(self, position):
        self.board[position[0],position[1]]=None
    
    def move_piece(self, start, end): # I should actually use move object here
        if self.board[start[0],start[1]]!=None and [[start[0], start[1]], [end[0], end[1]]] in self.get_valid_moves(): # should check for validness here
            move_made=move(start, end, self.board)
            # update king pos
            if isinstance(self.board[start[0], start[1]], king):
                if self.board[start[0], start[1]].color=='w':
                    self.white_king_loc=[end[0], end[1]]
                else:
                    self.black_king_loc=[end[0], end[1]]
            self.remove_piece(move_made.start)
            self.place_piece(move_made.end, move_made.piece_moved)
            self.move_log.append(move_made)
            self.whites_turn=(not self.whites_turn)
            print(self.move_log[-1])
        else:
            print("invalid move!")
    
    def undo_move(self):
        assert len(self.move_log)>=1, "move log is empty"
        last_move=self.move_log[-1]
        self.board[last_move.end[0], last_move.end[1]]=last_move.piece_captured
        self.board[last_move.start[0], last_move.start[1]]=last_move.piece_moved
        self.move_log.pop()
        self.whites_turn=not self.whites_turn
        # update king pos
        if last_move.piece_moved.key=='wK':
            self.white_king_loc=[last_move.start[0], last_move.start[1]]
        elif last_move.piece_moved.key=='bK':
            self.black_king_loc=[last_move.start[0], last_move.start[1]]
    
    def get_possible_moves(self):
        # generate a list of all possible moves
        moves=[]
        for row in range(BOARD_DIM):
            for col in range(BOARD_DIM):
                cur_obj=self.board[row, col]
                if cur_obj==None: continue
                else: moves+=cur_obj.get_moves(self, [row, col])
        
        return moves
    
    def get_valid_moves(self):
        # moves which end in a checkmate are not allowed and get filtered here
        
        new_gs=self.deep_copy()
        
        # valid_moves=[]
        
        # for move_1 in self.get_possible_moves():
            # new_gs.move_piece([move_1[0][0], move_1[0][1]], [move_1[1][0], move_1[1][1]])
            # for move_2 in new_gs.get_possible_moves():
                # new_gs.move_piece([move_2[0][0], move_2[0][1]], [move_2[1][0], move_2[1][1]])
                # if (not isinstance(new_gs.move_log[-1].piece_captured, king)):
                    # valid_moves.append(move_1)
                    # new_gs.undo_move()
                # else:
                    # new_gs.undo_move()
            # new_gs.undo_move()
        
        # return valid_moves
        
        return new_gs.get_possible_moves()
    
    def get_board(self):
        return self.board
    
    def state(self):
        return self.board
    
    def deep_copy(self):
        deep_copy=chess_board(self.id, self.whites_turn)
        deep_copy.set_board(self.board)
        deep_copy.set_move_log(self.move_log)
        return deep_copy
    
    def set_board(self, board):
        self.board=board
    
    def set_move_log(self, move_log):
        self.move_log=move_log
    
    def __str__(self):
        print(self.board)
    
    def __repr__(self):
        # implement a way to print board directly with None representatives
        print(self.board)
    
    def reset_board(self):
        for i in range(8):
            self.place_piece([1,i], pawn('w'))
            self.place_piece([6,i], pawn('b'))
        self.place_piece([0,0], rook('w'))
        self.place_piece([0,7], rook('w'))
        self.place_piece([7,0], rook('b'))
        self.place_piece([7,7], rook('b'))
        self.place_piece([0,1], knight('w'))
        self.place_piece([0,-2], knight('w'))
        self.place_piece([7,1], knight('b'))
        self.place_piece([7,-2], knight('b'))
        self.place_piece([0,2], bishop('w'))
        self.place_piece([7,2], bishop('b'))
        self.place_piece([0,-3], bishop('w'))
        self.place_piece([7,-3], bishop('b'))
        self.place_piece([0,4], king('w'))
        self.place_piece([7,4], king('b'))
        self.place_piece([0,3], queen('w'))
        self.place_piece([7,3], queen('b'))

class move: # class for storing moves and analyzing future moves
    def __init__(self, start, end, board):
        # store all the important information for a move
        # maybe also add boardstate, could be important for AI later on
        self.start=start
        self.end=end
        self.piece_moved=board[start[0], start[1]]
        # this direct approach for setting the piece captured is very intuitive
        # no peace captured would mean None dtype, and it simplifies some following implementations
        self.piece_captured=board[end[0], end[1]]
        
    def __repr__(self):
        return str(self.start+self.end)

class piece:
    def __init__(self, color):
        assert color=='w' or color=='b', "wrong/no color"
        self.color=color
    
    def add_horizontal_moves(self, board, pos):
        dir_1=[-1, 1]
        
        moves=[]
        
        for dir in dir_1:
            for row in range(1, BOARD_DIM):
                if 0 <= pos[0]+dir*row < BOARD_DIM:
                    if board[pos[0]+dir*row, pos[1]]==None:
                        moves.append([pos[0]+dir*row, pos[1]])
                    elif board[pos[0]+dir*row, pos[1]].color==self.color:
                        break
                    else:
                        moves.append([pos[0]+dir*row, pos[1]])
                        break
            for col in range(1, BOARD_DIM):
                if 0 <= pos[1]+dir*col < BOARD_DIM:
                    if board[pos[0], pos[1]+dir*col]==None:
                        moves.append([pos[0], pos[1]+dir*col])
                    elif board[pos[0], pos[1]+dir*col].color==self.color:
                        break
                    else:
                        moves.append([pos[0], pos[1]+dir*col])
                        break
        
        if len(moves)!=0:
            for i in range(len(moves)):
                moves[i]=[[pos[0], pos[1]],[moves[i][0], moves[i][1]]]
        
        return moves
    
    def add_diagonal_moves(self, board, pos):
        moves=[]

        directions_1=[-1,1]
        directions_2=[-1,1]
        
        for dir_1 in directions_1:
            for dir_2 in directions_2:
                for dist in range(1, BOARD_DIM):
                    if 0 <= pos[0]+dir_1*dist < BOARD_DIM and 0 <= pos[1]+dir_2*dist < BOARD_DIM:
                        if board[pos[0]+dir_1*dist, pos[1]+dir_2*dist]==None:
                            moves.append([pos[0]+dir_1*dist, pos[1]+dir_2*dist])
                        elif board[pos[0]+dir_1*dist, pos[1]+dir_2*dist].color==self.color:
                            break
                        else:
                            moves.append([pos[0]+dir_1*dist, pos[1]+dir_2*dist])
                            break
        
        if len(moves)!=0:
            for i in range(len(moves)):
                moves[i]=[[pos[0], pos[1]],[moves[i][0], moves[i][1]]]
        
        return moves
    
    def check_false_color_and_turn(self, whites_turn):
        if self.color=='b' and whites_turn:
            return True
            
        if self.color=='w' and (not whites_turn):
            return True
        
        else: return False
    
    def get_position(self):
        return self.position

class pawn(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='p'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        board=chess_board.get_board()
        moves=[]
        
        if self.color=='w' and chess_board.whites_turn:
            # catch the case when the pawn reached end position on the board
            assert pos[0]!=BOARD_DIM, "pawn must me promoted when end of board is reached"
            if  0 <= pos[0]+1 < BOARD_DIM and board[pos[0]+1, pos[1]]==None:
                moves.append([pos[0]+1, pos[1]])
                if 0 <= pos[0]+2 < BOARD_DIM and board[pos[0]+2, pos[1]]==None and pos in [[1,i] for i in range(BOARD_DIM)]:
                    moves.append([pos[0]+2, pos[1]])
            if 0 <= pos[0]+1 < BOARD_DIM and 0 <= pos[1]+1 < BOARD_DIM and board[pos[0]+1, pos[1]+1]!=None and board[pos[0]+1, pos[1]+1].color!=self.color:
                moves.append([pos[0]+1, pos[1]+1])
            if 0 <= pos[0]+1 < BOARD_DIM and 0 <= pos[1]-1 < BOARD_DIM and board[pos[0]+1, pos[1]-1]!=None and board[pos[0]+1, pos[1]-1].color!=self.color:
                moves.append([pos[0]+1, pos[1]-1])
        
        elif self.color=='b' and (not chess_board.whites_turn):
            assert pos[0]!=0, "pawn must me promoted when end of board is reached"
            if 0 <= pos[0]-1 < BOARD_DIM and board[pos[0]-1, pos[1]]==None:
                moves.append([pos[0]-1, pos[1]])
                if 0 <= pos[0]-2 < BOARD_DIM and board[pos[0]-2, pos[1]]==None and pos in [[6,i] for i in range(BOARD_DIM)]:
                    moves.append([pos[0]-2, pos[1]])
            if 0 <= pos[0]-1 < BOARD_DIM and 0 <= pos[1]-1 < BOARD_DIM and board[pos[0]-1, pos[1]-1]!=None and board[pos[0]-1, pos[1]-1].color!=self.color:
                moves.append([pos[0]-1, pos[1]-1])
            if 0 <= pos[0]-1 < BOARD_DIM and 0 <= pos[1]+1 < BOARD_DIM and board[pos[0]-1, pos[1]+1]!=None and board[pos[0]-1, pos[1]+1].color!=self.color:
                moves.append([pos[0]-1, pos[1]+1])
        
        # add beginning position 'pos' for comparing if the move is valid
        if len(moves)!=0:
            for i in range(len(moves)):
                moves[i]=[[pos[0], pos[1]],[moves[i][0], moves[i][1]]]
        
        return moves
    
    def __str__(self):
        return "P"
    
    def __repr__(self):
        return "P"

class rook(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='R'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        board=chess_board.get_board()
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return []
        
        return self.add_horizontal_moves(board, pos)
    
    
    def __str__(self):
        return "R"
    
    def __repr__(self):
        return "R"

class knight(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='N'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        moves=[]
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return moves
        
        board=chess_board.get_board()
        
        permutations=[[2,1],[1,2]]
        directions_1=[-1,1]
        directions_2=[-1,1]
        
        for dir_1 in directions_1:
            for dir_2 in directions_2:
                for perm in permutations:
                    if 0 <= pos[0]+dir_1*perm[0] < BOARD_DIM and 0 <= pos[1]+dir_2*perm[1] < BOARD_DIM:
                        if board[pos[0]+dir_1*perm[0], pos[1]+dir_2*perm[1]]==None or board[pos[0]+dir_1*perm[0], pos[1]+dir_2*perm[1]].color!=self.color:
                            moves.append([pos[0]+dir_1*perm[0], pos[1]+dir_2*perm[1]])
        
        if len(moves)!=0:
            for i in range(len(moves)):
                moves[i]=[[pos[0], pos[1]],[moves[i][0], moves[i][1]]]
        
        return moves
    
    def __str__(self):
        return "K"
    
    def __repr__(self):
        return "K"

class bishop(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='B'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
    
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return []
    
        board=chess_board.get_board()
        
        return self.add_diagonal_moves(board, pos)
    
    def __str__(self):
        return "B"
    
    def __repr__(self):
        return "B"

class queen(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='Q'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        moves=[]
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return moves
        
        board=chess_board.get_board()
        
        moves+=self.add_diagonal_moves(board, pos)
        moves+=self.add_horizontal_moves(board, pos)
        
        return moves
    
    def __str__(self):
        return "Q"
    
    def __repr__(self):
        return "Q"

class king(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='K'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        moves=[]
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return moves
        
        board=chess_board.get_board()
        
        directions_1=[-1,1]
        directions_2=[-1,1]
        
        for dir_1 in directions_1:
            for dir_2 in directions_2:
                pos_1=[pos[0]+dir_1, pos[1]]
                pos_2=[pos[0], pos[1]+dir_2]
                pos_3=[pos[0]+dir_1, pos[1]+dir_2]
                
                if 0 <= pos_1[0] < BOARD_DIM:
                    if board[pos_1[0], pos_1[1]]==None:
                        moves.append([pos_1[0], pos_1[1]])
                    elif board[pos_1[0], pos_1[1]].color==self.color:
                        break
                    else:
                        moves.append([pos_1[0], pos_1[1]])
                        break
                
                if 0 <= pos_2[1] < BOARD_DIM:
                    if board[pos_2[0], pos_2[1]]==None:
                        moves.append([pos_2[0], pos_2[1]])
                    elif board[pos_2[0], pos_2[1]].color==self.color:
                        break
                    else:
                        moves.append([pos_2[0], pos_2[1]])
                        break
                
                if 0 <= pos_3[0] < BOARD_DIM and 0 <= pos_3[1] < BOARD_DIM:
                    if board[pos_3[0], pos_3[1]]==None:
                        moves.append([pos_3[0], pos_3[1]])
                    elif board[pos_3[0], pos_3[1]].color==self.color:
                        break
                    else:
                        moves.append([pos_3[0], pos_3[1]])
                        break
        
        if len(moves)!=0:
            for i in range(len(moves)):
                moves[i]=[[pos[0], pos[1]],[moves[i][0], moves[i][1]]]
        
        return moves
    
    def __str__(self):
        return "X"
    
    def __repr__(self):
        return "X"

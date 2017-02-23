from core import Board, Player, Evaluator

def show_board(board):

    black_stonenum = len([1 for i in board.stones if i == -1])
    white_stonenum = len([1 for i in board.stones if i ==  1])
    print("black: {0} vs {1} :white".format(black_stonenum, white_stonenum))

    dispboard = ["2" if stone == -1 else "1" if stone == 1 else " " for stone in board.stones]
    for i in xrange(0, 8):
        offset = i * 8
        print(dispboard[offset:offset+8])


if __name__ == '__main__':

    evaluator = Evaluator()
    player = Player(evaluator)
    board = Board()

    while not board.check_gameover():
        mpos = player.move(board, -1)
        show_board(board)
        epos = player.move(board,  1)
        show_board(board)

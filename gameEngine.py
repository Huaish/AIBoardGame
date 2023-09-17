import time
import pandas
import argparse
from boardGenerate import createBoard

class Board:
    def __init__(self, input_file=None, data=None):
        '''
        Description:
            Initialize the board.
        Args:
            rows: number of rows
            cols: number of columns
            input_file: input file path
        Board structure:
            board: 0b
            mask:  0b111
            history_boards: [board1, board2, ...]
            moves: [(0, 'Row'), (1, 'Row'), ...] (all possible moves)
        '''
        if input_file:
            self.make_board_from_file(input_file)
        elif data:
            self.make_board(data)
        else:
            row, col, board = createBoard()
            self.rows = row
            self.cols = col
            self.board = 0
            self.mask = (1 << (row * col)) - 1
            for i in range(self.rows):
                for j in range(self.cols):
                    self.set(i, j, board[i][j])

        self.history_boards = []

        # Initialize all possible moves
        self.moves = []
        for i in range(self.rows):
            self.moves.append((i, 'Row'))
        for i in range(self.cols):
            self.moves.append((i, 'Column'))

    def make_board_from_file (self, input_file):
        '''
        Description:
            Initialize the board from input file.
        Args:
            input_file: input file path
        '''
        with open(input_file, "r") as file:
            line = file.readline()
            row, col = line.split()
            row, col = int(row), int(col)

            self.rows = row
            self.cols = col
            self.board = 0
            self.mask = (1 << (row * col)) - 1

            for i in range(row):
                line = file.readline().strip().split()
                for j in range(col):
                    self.set(i, j, int(line[j]))
    
    def make_board(self, data):
        '''
        Description:
            Initialize the board from data.
        Args:
            data: 2d array
        '''
        if data == None:
            self.rows = 0
            self.cols = 0
            self.board = 0

        self.rows = data[0][0]
        self.cols = data[0][1]
        data = data[1:]
        self.board = 0
        self.mask = (1 << (self.rows * self.cols)) - 1

        for i in range(self.rows):
            for j in range(self.cols):
                self.set(i, j, data[i][j])

    def get(self, x, y):
        '''
        Description:
            Get the value of the board at (x, y).
        Args:
            x: row index
            y: column index
        Return:
            0 or 1
        '''
        index = x * self.cols + y
        return (self.board >> index) & 1

    def set(self, x, y, value):
        '''
        Description:
            Set the value of the board at (x, y).
        Args:
            x: row index
            y: column index
            value: 0 or 1
        '''
        index = x * self.cols + y
        mask = 1 << index
        if value:
            # set 1
            self.board |= mask
        else:
            # set 0
            self.board &= ~mask
        self.board &= self.mask
    
    def remove_row(self, x):
        '''
        Description:
            Remove the row at x.
        Args:
            x: row index
        Return:
            number of 1 in the row
        '''
        # Calculate the number of 1 in the row
        row = self.board >> (x * self.cols) & ((1 << self.cols) - 1) 
        point = bin(row).count('1')
        mask = ((1 << self.cols) - 1) << (x * self.cols)
        self.board &= ~mask
        return point

    def remove_col(self, y):
        '''
        Description:
            Remove the column at y.
        Args:
            y: column index
        Return:
            number of 1 in the column
        '''
        point = 0
        for i in range(self.rows):
            if self.get(i, y):
                self.set(i, y, 0)
                point += 1
        return point

    def __str__(self):
        '''
        Description:
            Convert the board to string for printing.
        Return:
            string of the board (pandas.DataFrame)
        '''
        headerCol = ([chr(i) for i in range(ord('A'), ord('A') + self.cols)])
        headerRow = ([str(i) for i in range(1, self.rows + 1)])
        data = []
        for i in range(self.rows):
            row = [str(self.get(i, j)) for j in range(self.cols)]
            data.append(row)

        df = pandas.DataFrame(data, headerRow, headerCol)
        return str(df)
    
    def check(self):
        '''
        Description:
            Check if the board is empty.
        Return:
            True or False
        '''
        return self.board == 0

    def move(self, move):
        '''
        Description:
            Move the board.
        Args:
            move: (index, 'Row') or (index, 'Column')
        Return:
            number of 1 in the row or column
        '''
        self.history_boards.append(self.board)
        if move[1] == 'Row':
            return self.remove_row(move[0])
        elif move[1] == 'Column':
            return self.remove_col(move[0])
    
    def undo(self):
        '''
        Description:
            Undo the last move.
        '''
        if len(self.history_boards) > 0:
            self.board = self.history_boards.pop()

    def array(self):
        '''
        Description:
            Convert the board to 2d array.
        Return:
            2d array
        '''
        data = []
        for i in range(self.rows):
            row = [self.get(i, j) for j in range(self.cols)]
            data.append(row)
        return data

    def is_valid(self, move):
        '''
        Description:
            Check if the move is valid.
        Args:
            move: (index, 'Row') or (index, 'Column')
        Return:
            True or False
        '''
        if move[1] == 'Row':
            return move[0] >= 0 and move[0] < self.rows
        elif move[1] == 'Column':
            return move[0] >= 0 and move[0] < self.cols

class Engine:
    MAX, MIN = 1e9, -1e9

    def __init__(self, row=4, col=4, input_file=None, data=None):
        '''
        Description:
            Initialize the engine.
        Args:
            row: number of rows
            col: number of columns
            input_file: input file path
        '''
        if input_file:
            self.board = Board(input_file=input_file)
        elif data:
            self.board = Board(data=data)
        else:
            self.board = Board()
    
    def alpha_beta(self, maximiser=1, alpha=MIN, beta=MAX, point=0):
        '''
        Description:
            Alpha-beta pruning.
        Args:
            maximiser: 1 or -1
            alpha: alpha
            beta: beta
            point: current point
        Return:
            point, best step
        '''
        
        # Check if the game is over
        if self.board.check():
            return point, (-1, "End")
        
        # Get all possible moves
        moves = self.board.moves
        
        best_step = []
        if maximiser == 1: 
            # maximiser: choose the move with the maximum point
            max_point = Engine.MIN
            for step in moves:
                # move the board and calculate the point, then undo
                # if the move does not change the board, skip it
                p = self.board.move(step)
                if p == 0:
                    self.board.undo()    
                    continue
                p, _ = self.alpha_beta(-1, alpha, beta, point + p)
                self.board.undo()

                # update the best step and max_point
                if p > max_point:
                    max_point = p
                    best_step = step

                # update alpha and do alpha-beta pruning
                alpha = max(alpha, max_point)
                if beta <= alpha:
                    break
            return max_point, best_step

        else:
            # minimiser: choose the move with the minimum point
            min_point = Engine.MAX
            for step in moves:
                # move the board and calculate the point, then undo
                # if the move does not change the board, skip it
                p = self.board.move(step)
                if p == 0:
                    self.board.undo()
                    continue
                p, _ = self.alpha_beta(1, alpha, beta, point - p)
                self.board.undo()

                # update the best step and min_point
                if p < min_point:
                    min_point = p
                    best_step = step

                # update beta and do alpha-beta pruning
                beta = min(beta, min_point)
                if beta <= alpha:
                    break

            return min_point, best_step

def get_args():
    '''
    Description:
        Get arguments from command line.
    Return:
        args: arguments
    Args:
        -i: input file
        -o: output file
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default="input.txt", help="input file")
    parser.add_argument("-o", "--output", type=str, default="output.txt", help="output file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    input_file = args.input
    output_file = args.output

    game = Engine(input_file=input_file)
    start_time = time.time()
    point, step = game.alpha_beta()
    end_time = time.time()

    print(step[1], "# :", step[0] + 1)
    print(point, "points")
    print("Total run time:", end_time - start_time, "s")

    with open(output_file, 'w') as file:
        file.write(step[1] + " # : " + str(step[0] + 1) + "\n")
        file.write(str(point) + " points\n")
        file.write("Total run time:" + str(end_time - start_time) + " s\n")


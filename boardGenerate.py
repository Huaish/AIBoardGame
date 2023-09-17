import random
import numpy as np
import argparse

def createBoard():
    '''
    Description:
        Create a board with random numbers.
    '''
    row = random.randint(3, 8)
    col = random.randint(3, 8)
    arr = np.empty((row, col), dtype=int)
    for i in range(row):
        for j in range(col):
            arr[i][j] = random.getrandbits(1)
    return row, col, arr

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("row", help="number of rows")
    parser.add_argument("col", help="number of cols")
    parser.add_argument("output", help="output file")
    args = parser.parse_args()

    row = int(args.row)
    col = int(args.col)

    arr = np.empty((row, col), dtype=int)

    for i in range(row):
        for j in range(col):
            arr[i][j] = random.getrandbits(1)

    with open(args.output, 'w') as f:
        f.write(str(row) + " " + str(col) + "\n")
        for i in range(row):
            for j in range(col):
                f.write(str(arr[i][j]) + " ")
            f.write("\n")

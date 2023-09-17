import time
from flask import Flask, render_template, request, redirect, url_for, jsonify
from gameEngine import Engine

app = Flask(__name__)
engine = Engine()
points = {
    "Player": 0,
    "AI": 0
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def uploadBoard():
    '''
    Description:
        Create a board from the uploaded file.
        Also, do the alpha-beta pruning and output the result to output.txt.
    Args:
        file: the uploaded file
    Return:
        JSON response {
            "rows": number of rows,
            "cols": number of columns,
            "board": board data
        }     
    '''
    global engine
    global points

    # Get the file from the POST request
    data = request.files['file']
    boardData = [ [int(x) for x in line.split()] for line in data ]

    # Initialize engine and points
    engine = Engine(data=boardData)

    # Do alpha-beta pruning and output the result to output.txt
    start_time = time.time()
    point, step = engine.alpha_beta()
    end_time = time.time()
    with open("output.txt", "w") as f:
        f.write(step[1] + " # : " + str(step[0] + 1) + "\n")
        f.write(str(point) + " points\n")
        f.write("Total run time: " + str(end_time - start_time) + " s\n")

    # Initialize points
    points = {
        "Player": 0,
        "AI": 0
    }

    # Return response
    res = {
        "rows": engine.board.rows,
        "cols": engine.board.cols,
        "board": engine.board.array()
    }
    return jsonify(res)

@app.route('/create', methods=['GET'])
def newGame():
    '''
    Description:
        Create a board with random numbers.
    Return:
        JSON response {
            "rows": number of rows,
            "cols": number of columns,
            "board": board data
        }
    '''
    global engine
    global points
    engine = Engine()
    print(engine.board)
    points = {
        "Player": 0,
        "AI": 0
    }
    res = {
        "success": True,
        "rows": engine.board.rows,
        "cols": engine.board.cols,
        "board": engine.board.array()
    }
    return jsonify(res)


@app.route('/move', methods=['POST'])
def move():
    '''
    Description:
        Move the board according to the step.
    Args:
        direction: "row" or "col"
        index: index of the row/col
    Return:
        JSON response {
            "success": True/False,
            "rows": number of rows,
            "cols": number of columns,
            "board": board data
        }
    '''
    global engine
    global points
    content = request.json

    direction = content["direction"]
    direction = "Row" if direction == "row" else "Column"
    index = content["index"]
    index = int(index) - 1
    step = (index, direction)

    if engine.board.is_valid(step):
        points["Player"] += engine.board.move(step)
        res = {
            "success": True,
            "rows": engine.board.rows,
            "cols": engine.board.cols,
            "board": engine.board.array(),
        }
        return jsonify(res)
    else:
        return jsonify({
            "success": False,
            "message": "Step is invalid!"
        })

@app.route('/check', methods=['GET'])
def check():
    '''
    Description:
        Check if the game is over.
    Return:
        JSON response {
            "success": True/False,
            "check": True/False,
            "message": "Player wins!" or "AI wins!" or "Tie!"
        }
    '''
    global engine
    global points
    winner = "Tie"
    if points["Player"] < points["AI"]:
        winner = "AI"
    else:
        winner = "Player"

    res = {
        "success": True,
        "check": engine.board.check(),
        "message": winner + " wins!" if winner != "Tie" else "Tie!"
    }
    return jsonify(res)

@app.route('/AI', methods=['GET'])
def AI():
    '''
    Description:
        AI move.
    Return:
        JSON response {
            "success": True/False,
            "rows": number of rows,
            "cols": number of columns,
            "board": board data
        }
    '''
    global engine
    global points
    point, step = engine.alpha_beta()
    points["AI"] += point
    engine.board.move(step)
    res = {
        "success": True,
        "rows": engine.board.rows,
        "cols": engine.board.cols,
        "board": engine.board.array()
    }
    return jsonify(res)

@app.route('/points', methods=['GET'])
def getPoints():
    '''
    Description:
        Get the current points.
    Return:
        JSON response {
            "player": player points,
            "AI": AI points
        }
    '''
    global points
    res = {
        "player": points["Player"],
        "AI": points["AI"]
    }
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
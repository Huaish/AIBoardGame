var bar = document.getElementById('js-progressbar');

async function updateBoard(rows, cols, boardData) {
    var board = document.getElementById('board');
    var html = '';

    var size = board.clientWidth;
    var squareSize = size / (cols + 1);

    // add A - H notation
    html += '<div class="row-board">';
    html += '<div class="square" style="width: ' + squareSize + 'px; height: ' + squareSize + 'px;">' + '</div>';
    for (var i = 0; i < cols; i++) {
        html += '<div class="col-' + (i + 1);
        html += ' square notation" ';
        html += 'id="col-' + (i + 1) + '" ';
        html += 'style="width: ' + squareSize + 'px; height: ' + squareSize + 'px;"'
        html += 'onmouseover="onHover(event)" onmouseout="onHoverOut(event)" onClick="move(event)">';
        html += String.fromCharCode(65 + i) + '</div>';
    }
    html += '</div>';

    for (var i = 0; i < rows; i++) {
        html += '<div class="row-board row-' + (i + 1) + '">';
        html += '<div class="row-' + (i + 1);
        html += ' square notation" ';
        html += 'id="row-' + (i + 1) + '" ';
        html += 'style="width: ' + squareSize + 'px; height: ' + squareSize + 'px;"'
        html += 'onmouseover="onHover(event)" onmouseout="onHoverOut(event)" onClick="move(event)">';
        html += (i + 1) + '</div>';

        for (var j = 0; j < cols; j++) {
            if (boardData[i][j] == 1) {
                html += '<div class="square col-' + (j + 1) + '" ';
                html += 'id="square-' + i + '-' + (j + 1) + '"  style="width: ' + squareSize + 'px; height: ' + squareSize + 'px;">';
                html += '<div class="circle"></div>';
                html += '</div>';
            }
            else {
                html += '<div class="square col-' + (j + 1) + '" ';
                html += 'id="square-' + i + '-' + (j + 1) + '"  style="width: ' + squareSize + 'px; height: ' + squareSize + 'px;">';
                html += '<div class=""></div>';
                html += '</div>';
            }
        }
        html += '</div>';
    }

    board.innerHTML = html;

}

async function createBoard() {
    var res = await fetch('/create');
    res = await res.json();
    if (res.success) {
        await updateBoard(res.rows, res.cols, res.board);
    }
    else {
        alert(res.message);
    }
    await updatePoints();
}

UIkit.upload('.js-upload', {

    url: 'upload',
    multiple: false,
    method: 'POST',
    name: 'file',
    params: { enctype: "multipart/form-data" },

    complete: async function (res) {
        res = JSON.parse(res.response);
        await updateBoard(res.rows, res.cols, res.board);
    },

    loadStart: function (e) {
        bar.removeAttribute('hidden');
        bar.max = e.total;
        bar.value = e.loaded;
    },

    progress: function (e) {
        bar.max = e.total;
        bar.value = e.loaded;
    },

    loadEnd: function (e) {
        bar.max = e.total;
        bar.value = e.loaded;
    },

    completeAll: function () {
        setTimeout(function () {
            bar.setAttribute('hidden', 'hidden');
        }, 1000);
    }

});

async function check() {
    var res = await fetch('/check');
    res = await res.json();
    if (res.success) {
        if (res.check) {
            alert('Game over\n' + res.message);
        }
    }

    return res.check;
}

async function move(event) {
    document.getElementById('board').classList.toggle('disabledbutton');
    var id = event.target.id;
    direction = id.split('-')[0];
    index = id.split('-')[1];

    var res = await fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            direction: direction,
            index: index
        })
    });
    res = await res.json();
    if (res.success) {
        await updateBoard(res.rows, res.cols, res.board);
    }
    else {
        alert(res.message);
    }

    await updatePoints();

    setTimeout(async function () {
        gameOver = await check();
        if (!gameOver) {
            changePlayer("AI");
            setTimeout(function () {
                AI_move();
            }, 1000);
        }
    }, 1000);
}

async function updatePoints() {
    var res = await fetch('/points');
    res = await res.json();
    document.getElementById('player-point').innerHTML = res.player;
    document.getElementById('AI-point').innerHTML = res.AI;

}

async function AI_move() {
    var res = await fetch('/AI');
    res = await res.json();
    if (res.success) {
        await updateBoard(res.rows, res.cols, res.board);
    }
    else {
        alert(res.message);
    }
    await updatePoints();

    setTimeout(async function () {
        gameOver = await check();
        if (!gameOver)
            changePlayer("Player");
    }, 1000);
    document.getElementById('board').classList.toggle('disabledbutton');
}

function changePlayer(nowTurn) {
    document.getElementById('status').innerHTML = nowTurn + "'s turn";
}

var onHover = function (event) {
    var selected = event.target.classList[0];
    var squares = document.getElementsByClassName(selected);
    for (var i = 0; i < squares.length; i++) {
        squares[i].classList.add('focus');
    }
}

var onHoverOut = function (event) {
    var selected = event.target.classList[0];
    var squares = document.getElementsByClassName(selected);
    for (var i = 0; i < squares.length; i++) {
        squares[i].classList.remove('focus');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    createBoard();
}, false);

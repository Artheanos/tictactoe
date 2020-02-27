let canvas = document.getElementsByTagName('canvas')[0];

let width = 300;
let height = 300;

canvas.width = width;
canvas.height = height;

let ctx = canvas.getContext('2d');

function draw_line(x0, y0, x1, y1) {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.lineWidth = 3;
    ctx.stroke();
}

function draw_board() {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = 'rgb(100, 0, 100)';

    for (let i = 0; i < 2; i++) {
        draw_line(width / 3 * (i + 1), 0, width / 3 * (i + 1), height);
        draw_line(width / 3 * (i + 1), 0, width / 3 * (i + 1), height);
        draw_line(0, height / 3 * (i + 1), width, height / 3 * (i + 1));
        draw_line(0, height / 3 * (i + 1), width, height / 3 * (i + 1));
    }

    draw_pawns();
}

function _draw_cross(x, y) {
    ctx.fillStyle = 'rgb(0, 0, 100)';
    let r = 40;
    draw_line(x - r, y + r, x + r, y - r);
    draw_line(x - r, y - r, x + r, y + r);
}

function _draw_circle(x, y) {
    ctx.fillStyle = 'rgb(0, 0, 100)';
    let r = 40;
    ctx.moveTo(x + r, y);
    ctx.arc(x, y, r, 0, 2 * Math.PI);
    ctx.stroke();
}

function draw_pawns() {
    for (let i = 0; i < 9; i++) {
        if (board_state.charAt(i) === '1')
            _draw_circle(i % 3 * width / 3 + width / 6, Math.floor(i / 3) * height / 3 + height / 6);
        else if (board_state.charAt(i) === '2')
            _draw_cross(i % 3 * width / 3 + width / 6, Math.floor(i / 3) * height / 3 + height / 6);
    }
}
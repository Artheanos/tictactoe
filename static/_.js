document.onkeydown = function (e) {

    console.log(e.key);

    if (e.key === 'ArrowUp') {
        //canvas.height -= 100;
        y -= 50;
    }
    if (e.key === 'ArrowDown') {
        //canvas.height += 100;
        y += 50;
    }
    if (e.key === 'ArrowLeft') {
        //canvas.width += 100;
        x -= 50;
    }
    if (e.key === 'ArrowRight') {
        //canvas.width -= 100;

        x += 50;
    }
};

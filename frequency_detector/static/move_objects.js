function moveLeft() {
var element = document.getElementById("image1");
element.style.left = parseInt(element.style.left) - 5 + 'px';
};

function moveRight() {
var element = document.getElementById("image1");
element.style.left = parseInt(element.style.left) + 5 + 'px';

};

function moveUp() {
var element = document.getElementById("image1");
element.style.top = parseInt(element.style.top) - 5 + 'px';
};

function moveDown() {
var element = document.getElementById("image1");
element.style.top = parseInt(element.style.top) + 5 + 'px';
};

function moveSelection(string) {
    switch (string) {
        case "400<freq<450 hz: left":
        moveLeft();
        break;
        case "450<freq<500 hz: right":
        moveRight();
        break;
        case "300<freq<350 hz: up":
        moveUp();
        break;
        case "350<freq<400 hz: down":
        moveDown();
        break;
        };
    };
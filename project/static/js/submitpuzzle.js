$(document).ready(function(){

    //Function to slide down the instructions information
    let instr = document.querySelector("#instructions");
    $("#showInstructions").click(function(){
        instr.dataset.display = instr.dataset.display === "false";
    });
});

let titleInput, titleFace, contentInput, contentFace, submitInput, submitFace;

window.addEventListener('load', function() {
    titleInput = document.getElementById("puzzlename");
    contentInput = document.getElementById("puzzle");
    titleFace = document.getElementById("puzzle-name-input");
    contentFace = document.getElementById("content-box");
    submitInput = document.getElementById("submit");
    submitFace = document.getElementById("create-puzzle-btn");

    submitFace.addEventListener('click', function() {
        submitInput.click();
    })

    titleFace.addEventListener('click', function() {
        titleInput.focus();
        titleInput.setSelectionRange(titleInput.value.length, titleInput.value.length);
    })

    contentFace.addEventListener('click', function() {
        contentInput.focus();
        contentInput.setSelectionRange(contentInput.value.length, contentInput.value.length);
    });

    titleInput.addEventListener('input', function () {
        titleInput.value = titleInput.value.slice(0,40);
        updateTitle(titleInput.value);
    })

    contentInput.addEventListener('input', function () {
        let n = '';
        for (char of contentInput.value.split('')) {
            if( char.toUpperCase() != char.toLowerCase() ) {
                n += char;
            }
        }
        contentInput.value = n.slice(0,10);
        updateContent(contentInput.value);
    })
    updateTitle(titleInput.value);
    updateContent(contentInput.value);

    titleFace.setAttribute('selected', false);
    titleInput.addEventListener('focus', function(){
        titleFace.setAttribute('selected', true);
    })
    titleInput.addEventListener('focusout', function(){
        titleFace.setAttribute('selected', false);
    })

    contentFace.setAttribute('selected', false);
    contentInput.addEventListener('focus', function(){
        contentFace.setAttribute('selected', true);
    })
    contentInput.addEventListener('focusout', function(){
        contentFace.setAttribute('selected', false);
    })
})

function updateContent(text) {
    for (let i = 0; i < 10; i++) {
        let id = 'ls' + (i+1);
        let box = document.getElementById(id);
        if (i < text.length) {
            box.textContent = text[i].toLowerCase();
            box.classList.add("has-text");
        } else {
            box.textContent = '';
            box.classList.remove("has-text");
        }
        
    }
}

function updateTitle(title) {
    if (title == '') {
        titleFace.setAttribute('empty', 'true');
    } else {
        titleFace.setAttribute('empty', 'false');
    }
    titleFace.textContent = title;
}
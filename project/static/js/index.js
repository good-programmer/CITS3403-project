

window.onload = function(){
    console.log('yes');
    const puzTable = document.getElementById("puz-table");

    const puzzle = document.createElement("div");

    puzzle.classList.add("post");
    puzzle.textContent = "yes";

    puzTable.append(puzzle)

}


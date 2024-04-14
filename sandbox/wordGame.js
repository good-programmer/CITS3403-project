let randomString = generateRandomString(15);
let displayString = randomString
let submittedWords = [];
let shuffleInterval;
let selectedWord = -1;


document.getElementById('randomString').innerText = displayString.toUpperCase();

/* keep userInput in focus */
document.getElementById('userInput').addEventListener('blur', function() {
    setTimeout(function() { document.getElementById('userInput').focus(); }, 0);
});

/* placeholder for user generated 'puzzles' - return 15 random chars */
function generateRandomString(length) {
    let result = '';
    let characters = 'abcdefghijklmnopqrstuvwxyz';
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

/* give user ability to shuffle the puzzle string */
function shuffleString() {
    let array = randomString.split('');
    for (let i = array.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    randomString = array.join('');
    document.getElementById('randomString').innerText = randomString.toUpperCase();
    document.getElementById('userInput').value = ''; // clear the user input
}

/* if the user enters a char from the puzzle string, remove it from the display */
function updateString() {
    let userInput = document.getElementById('userInput').value;
    let tempString = randomString;
    for (let i = 0; i < userInput.length; i++) {
        let lowerCaseChar = userInput[i].toLowerCase();
        if (tempString.includes(lowerCaseChar)) {
            tempString = tempString.replace(lowerCaseChar, '');
        } else {
            // remove the character from userInput if it's not in the random string
            document.getElementById('userInput').value = userInput.slice(0, i) + userInput.slice(i + 1);
            return;
        }
    }
    displayString = tempString;
    document.getElementById('randomString').innerText = displayString.toUpperCase();
}

document.getElementById('userInput').addEventListener('keydown', function(event) {
    if (event.key === 'ArrowUp') {
        if (selectedWord === -1) {
            selectedWord = submittedWords.length;
        }
    }
    
    if (event.key === 'Enter') {
        event.preventDefault();
        let word = document.getElementById('userInput').value;
        if (word !== '') {
            submittedWords.push(word);
            // check the length of submittedWords after a word is added
            if (submittedWords.length > 5) {
                // if length exceeds 5, remove the last word added
                submittedWords.pop();
                return;
            }
            updateSubmittedWords();
            document.getElementById('userInput').value = '';
            displayString = randomString; // reset the display string to the shuffled string
            document.getElementById('randomString').innerText = displayString.toUpperCase();
        }
    }
});

function updateSubmittedWords() {
    if (submittedWords.length <= 5) {
        const container = document.getElementById('submittedWords');
        container.innerHTML = '';
        submittedWords.forEach((word, index) => {
            let div = document.createElement('div');
            div.className = 'wordTile MatrixTextGreen';
            div.style.cursor = 'pointer';
            let p = document.createElement('p');
            p.innerText = word;
            p.style.display = 'inline-block';
            div.appendChild(p);
            container.appendChild(div);

            div.addEventListener('click', function() {
                submittedWords.splice(index, 1);
                updateSubmittedWords();
            });

            div.addEventListener('mouseover', function() {
                p.innerText = word + ' [DELETE?]';
                div.classList.add('MatrixTextRed');
            });

            div.addEventListener('mouseout', function() {
                p.innerText = word;
                div.classList.remove('MatrixTextRed');
            });
        });
    }
}

// implements 'click and hold' shuffleButton
document.getElementById('shuffleButton').addEventListener('mousedown', function() {
    // start shuffling when the button is pressed
    shuffleInterval = setInterval(shuffleString, 100);
});

document.getElementById('shuffleButton').addEventListener('mouseup', function() {
    // stop shuffling when the button is released
    clearInterval(shuffleInterval);
});


// highlight shuffleButton on hover
document.getElementById('shuffleButton').addEventListener('mouseover', function() {
    this.classList.add('MatrixTextYellow')
});

document.getElementById('shuffleButton').addEventListener('mouseout', function() {
    clearInterval(shuffleInterval);
    this.classList.remove('MatrixTextYellow')
});
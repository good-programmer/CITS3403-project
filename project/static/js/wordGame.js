let randomString = generateRandomString(15);
let displayString = randomString
let submittedWords = [];
let shuffleInterval;

let score = 0;

window.onload = function() {
    // allocate enough width for double digit score
    let scoreElement = document.getElementById('score');
    let oneCharWidth = scoreElement.offsetWidth / 8;
    scoreElement.style.width = (oneCharWidth * 9) + 'px';

    let shuffleButton = document.getElementById('shuffleButton');
    let resetButton = document.getElementById('resetButton');
    let userInput = document.getElementById('userInput')

    // disable user inputs while animation plays
    shuffleButton.disabled = true;
    resetButton.disabled = true;
    userInput.disabled = true;

    // animate randomString to appear letter by letter
    let i = 0;
    let animInterval = setInterval(function() {
        if (i < displayString.length) {
            document.getElementById('randomString').innerText += displayString[i].toUpperCase();
            i++;
        } else {
            clearInterval(animInterval);
            // enable user inputs
            shuffleButton.disabled = false;
            resetButton.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
    }, 30);
}

document.getElementById('randomString').innerText = '';
document.getElementById('scoreValue').innerText = score;

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
    if (event.key === 'Backspace' ) {
        document.getElementById('userInput').classList.remove('MatrixTextRed');
    }
    if (event.key === 'Enter') {
        event.preventDefault();
        let word = document.getElementById('userInput').value.toLowerCase();
        if (word !== '') {

            // Check if the word is already in submittedWords
            if (submittedWords.includes(word)) {
                console.log('Duplicate word')
                // reset input and randomString
                document.getElementById('userInput').value = '';
                displayString = randomString; // reset the display string to the shuffled string
                document.getElementById('randomString').innerText = displayString.toUpperCase();
                return;
            }
            submittedWords.push(word);
            // check the length of submittedWords after a word is added
            if (submittedWords.length > 5) {
                // if length exceeds 5, remove the last word added
                submittedWords.pop();
                return;
            }

            // send user input to the server
            fetch('/wordGame', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'userInput=' + encodeURIComponent(word),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.is_valid) {
                    // The word is valid, update the submitted words and score
                    updateSubmittedWords();
                    updateScore();
                    // reset input and randomString
                    document.getElementById('userInput').value = '';
                    displayString = randomString; // reset the display string to the shuffled string
                    document.getElementById('randomString').innerText = displayString.toUpperCase();
                } else {
                    console.log('Invalid word');
                    document.getElementById('userInput').classList.add('MatrixTextRed')
                    submittedWords.pop();
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    }
});

function updateSubmittedWords() {
    if (submittedWords.length <= 5) {
        const container = document.getElementById('submittedWords');
        container.innerHTML = '';
        submittedWords.forEach((word, index) => {
            let div = document.createElement('div');
            div.className = 'wordTile Screen MatrixTextGreen';
            div.style.cursor = 'pointer';
            let p = document.createElement('p');
            p.innerText = word;
            p.style.display = 'inline-block';
            div.appendChild(p);
            container.appendChild(div);

            div.addEventListener('click', function() {
                submittedWords.splice(index, 1);
                updateSubmittedWords();
                updateScore();
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

function updateScore() {
    score = submittedWords.reduce((total, word) => total + word.length, 0);
    document.getElementById('scoreValue').innerText = score;
}

function reset() {
    score = 0;
    document.getElementById('scoreValue').innerText = score;
    submittedWords = [];
    updateSubmittedWords();
    document.getElementById('userInput').value = '';
    document.getElementById('userInput').classList.remove('MatrixTextRed');
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

// highlight resetButton on hover
document.getElementById('resetButton').addEventListener('mouseover', function() {
    this.classList.add('MatrixTextRed')
});

document.getElementById('resetButton').addEventListener('mouseout', function() {
    clearInterval(shuffleInterval);
    this.classList.remove('MatrixTextRed')
});

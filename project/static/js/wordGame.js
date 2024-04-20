let Game = {
    score: 0,
    puzzleString: '',
    displayString: '',
    submittedWords: [],
    shuffleInterval: null,
    shuffleSpeed: 100,      // adjusts shuffleString speed on mousedown
    animationSpeed: 30,     // adjusts animatePuzzleString speed
    
    /* placeholder for user generated 'puzzles' - return 15 random chars.
       eventually replace this with string associated with puzzle db*/
    generateRandomString: function(length) {
        let result = '';
        let characters = 'abcdefghijklmnopqrstuvwxyz';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    },

    // animate puzzleString to appear letter by letter
    animatePuzzleString: function() {
        let shuffleButton = document.getElementById('shuffleButton');
        let resetButton = document.getElementById('resetButton');
        let userInput = document.getElementById('userInput')
    
        // disable user inputs while animation plays
        shuffleButton.disabled = true;
        resetButton.disabled = true;
        userInput.disabled = true;

        // 'animation'
        let i = 0;
        let animInterval = setInterval(() => {
            if (i < this.displayString.length) {
                document.getElementById('puzzleString').innerText += this.displayString[i].toUpperCase();
                i++;
            } else {
                clearInterval(animInterval);

                // enable user inputs
                shuffleButton.disabled = false;
                resetButton.disabled = false;
                userInput.disabled = false;
                userInput.focus();
            }
        }, this.animationSpeed);
    },
    
    updateScore: function() {
        this.score = this.submittedWords.reduce((total, word) => total + word.length, 0);
        document.getElementById('scoreValue').innerText = this.score;
    },

    // dynamically create elements for user submitted words
    updateSubmittedWords: function() {
        if (this.submittedWords.length <= 5) {
            const container = document.getElementById('submittedWords');
            container.innerHTML = '';
            this.submittedWords.forEach((word, index) => {
                let div = document.createElement('div');
                div.className = 'wordTile Screen MatrixTextGreen';
                div.style.cursor = 'pointer';
                let p = document.createElement('p');
                p.innerText = word;
                p.style.display = 'inline-block';
                div.appendChild(p);
                container.appendChild(div);
    
                div.addEventListener('click', () => {
                    this.submittedWords.splice(index, 1);
                    this.updateSubmittedWords();
                    this.updateScore();
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
    },

    // remove chars from displayString as the user types their word
    updateString: function() {
        let userInput = document.getElementById('userInput').value;
        let tempString = Game.puzzleString;
        for (let i = 0; i < userInput.length; i++) {
            let lowerCaseChar = userInput[i].toLowerCase();
            if (tempString.includes(lowerCaseChar)) {
                tempString = tempString.replace(lowerCaseChar, '');
            } else {
                // remove the character from userInput if it's not in the puzzleString
                document.getElementById('userInput').value = userInput.slice(0, i) + userInput.slice(i + 1);
                return;
            }
        }
        this.displayString = tempString;
        document.getElementById('puzzleString').innerText = this.displayString.toUpperCase();
    },

    // shuffle the order of puzzleString chars
    shuffleString: function() {
        let array = this.puzzleString.split('');
        for (let i = array.length - 1; i > 0; i--) {
            let j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        this.puzzleString = array.join('');
        document.getElementById('puzzleString').innerText = this.puzzleString.toUpperCase();
        document.getElementById('userInput').value = ''; // clear the user input
    },

    // set game back to start state
    reset: function() {
        document.getElementById('scoreValue').innerText = score;
        this.submittedWords = [];
        this.updateSubmittedWords();
        this.updateScore();
        document.getElementById('userInput').value = '';
        document.getElementById('userInput').classList.remove('MatrixTextRed');
    },

    // sets EventListeners for word submission
    setUserInputs: function() {
        document.getElementById('userInput').addEventListener('keydown', (event) => {
            // 'Enter' - user submitting word
            if (event.key === 'Enter') {
                event.preventDefault();
                let word = document.getElementById('userInput').value.toLowerCase();
                if (word !== '') {
    
                    // check if the word is already in submittedWords
                    if (this.submittedWords.includes(word)) {
                        console.log('Duplicate word')
                        return;
                    }
                    // check the length of submittedWords after a word is added
                    if (this.submittedWords.length + 1 > 5) {
                        console.log('Too many submittedWords')
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
                            console.log('Valid word');
                            this.submittedWords.push(word);
                            this.updateSubmittedWords();
                            this.updateScore();
                            // reset input and puzzleString
                            document.getElementById('userInput').value = '';
                            this.displayString = this.puzzleString; // reset the display string to the shuffled string
                            document.getElementById('puzzleString').innerText = this.displayString.toUpperCase();
                        } else {
                            console.log('Invalid word');
                            document.getElementById('userInput').classList.add('MatrixTextRed')
                        }
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
                }
            }
            // 'Backspace' - remove red highlighting from incorrect word submission
            if (event.key === 'Backspace' ) {
                document.getElementById('userInput').classList.remove('MatrixTextRed');
            }
        });
    },

    // initialise game
    init: function () {
        Game.animatePuzzleString();
        Game.setUserInputs();
        Game.puzzleString = Game.generateRandomString(15);
        Game.displayString = Game.puzzleString;
        Game.updateScore();

        // allocate enough width for double digit score
        let scoreElement = document.getElementById('score');
        let oneCharWidth = scoreElement.offsetWidth / 8;
        scoreElement.style.width = (oneCharWidth * 9) + 'px';

        // keep userInput in focus
        document.getElementById('userInput').addEventListener('blur', function() {
            setTimeout(function() { document.getElementById('userInput').focus(); }, 0);
        });
    }
}

function setEventListeners() {
    // implements 'click and hold' shuffleButton
    document.getElementById('shuffleButton').addEventListener('mousedown', function() {
        // start shuffling when the button is pressed
        Game.shuffleInterval = setInterval(() => { Game.shuffleString(); }, 100); // Changed here
    });

    document.getElementById('shuffleButton').addEventListener('mouseup', function() {
        // stop shuffling when the button is released
        clearInterval(Game.shuffleInterval);
    });

    // highlight shuffleButton on hover
    document.getElementById('shuffleButton').addEventListener('mouseover', function() {
        this.classList.add('MatrixTextYellow')
    });

    document.getElementById('shuffleButton').addEventListener('mouseout', function() {
        clearInterval(Game.shuffleInterval);
        this.classList.remove('MatrixTextYellow')
    });

    // highlight resetButton on hover
    document.getElementById('resetButton').addEventListener('mouseover', function() {
        this.classList.add('MatrixTextRed')
    });

    document.getElementById('resetButton').addEventListener('mouseout', function() {
        clearInterval(Game.shuffleInterval);
        this.classList.remove('MatrixTextRed')
    });
}

window.onload = function() {
    Game.init();
    setEventListeners();
}

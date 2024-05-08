let Game = {
    puzzleid: null,
    solved: false,
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

    getPuzzleString: function () {
        return document.getElementById("puzzleStringContainer").dataset.puzzlestring
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
        let tempString = Game.puzzleString.toLowerCase();
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

    solve: function() {
        if (!Game.solved) {
            let solveData = {
                submittedWords: this.submittedWords,
                date: new Date()
            };

            let jsonData = JSON.stringify(solveData);

            fetch('/puzzle/' + Game.puzzleid + '/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: jsonData,
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        Game.solved = true;
        displayLeaderboard();
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
                    fetch('/puzzle/' + Game.puzzleid + '/play', {
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
                            // the word is valid, update the submitted words and score
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
    init: async function () {
        Game.puzzleid = window.location.pathname.split('/')[2];
        Game.animatePuzzleString();
        Game.setUserInputs();
        Game.puzzleString = Game.getPuzzleString();
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
        this.classList.remove('MatrixTextRed')
    });

    // highlight submitButton on hover
    document.getElementById('submitButton').addEventListener('mouseover', function() {
        this.classList.remove('MatrixTextYellow')
        this.classList.add('MatrixTextGreen')
    });

    document.getElementById('submitButton').addEventListener('mouseout', function() {
        this.classList.remove('MatrixTextGreen')
        this.classList.add('MatrixTextYellow')
    });
}

window.onload = function() {
    Game.init();
    setEventListeners();
}

function displayLeaderboard() {
    // hide the game content
    $('#gameContent').hide();
    $('#userInput').prop('disabled', true);
    $('#submittedWords').find('div').css('pointer-events', 'none');

    // create new div for the leaderboard
    let leaderboardDiv = $('<div>').attr('id', 'leaderboard');
    leaderboardDiv.addClass('container Screen MatrixTextYellow')

    // create a table
    let table = $('<table>').addClass('leaderboard-table');

    // create leadboard table
    let thead = $('<thead>');
    thead.append($('<tr>')
        .append($('<th>').text('RANK'))
        .append($('<th>').text('NAME'))
        .append($('<th>').text('SCORE'))
    );
    table.append(thead);

    let tbody = $('<tbody>');

    $.ajax({
        url: '/puzzle/' + Game.puzzleid + '/lite-leaderboard',
        type: 'GET',
        success: function(data) {
        
            leaderboardDiv.append($('<h2>').text('LEADERBOARD'));

            // display the leaderboard
            for (let i = 0; i < data.leaderboard.length; i++) {
                let username = data.leaderboard[i].username;
                if (username.length > 20) {
                    username = username.substring(0, 17) + '...';
                }
                let userLink = $('<a>').attr('href', '/user/' + data.leaderboard[i].userID + '/profile').text(username);
                userLink.addClass('MatrixTextYellow');
                tbody.append($('<tr>')
                    .append($('<td>').text(i + 1))                      // RANK
                    .append($('<td>').append(userLink))                 // USER
                    .append($('<td>').text(data.leaderboard[i].score))  // SCORE
                );
            }
            let currentUserRow = $('<tr>')
                .append($('<td>').text(data.currentUser.rank))
                .append($('<td>').text(data.currentUser.username))
                .append($('<td>').text(data.currentUser.score));
            currentUserRow.addClass('MatrixTextGreen');
            tbody.append(currentUserRow);
            table.append(tbody);
    
            // add table to the leaderboard div
            leaderboardDiv.append(table);

            // create a button for closing the leaderboard
            let closeButton = $('<button>').text('[SHOW PUZZLE]');
            closeButton.addClass('Screen MatrixTextYellow Button');
            closeButton.attr('id', 'closeButton');
    
            // create a button for exiting the game
            let exitButton = $('<button>').text('[EXIT]');
            exitButton.addClass('Screen MatrixTextYellow Button');
            exitButton.attr('id', 'exitButton');
    
            // create a div to contain the buttons
            let buttonContainer = $('<div>').attr('id', 'buttonContainer');
            buttonContainer.append(closeButton, exitButton);
            leaderboardDiv.append(buttonContainer);

            $('#closeButton').click(function() {
                $('#leaderboard').remove();
                $('#gameContent').show();
                $('#shuffleButton').remove();
                $('#resetButton').remove();
            });
        
            $('#exitButton').click(function() {
                window.location.href = '/profile';
            });
        }
    });
    
    // add leaderboard to page
    $('#gameArea').append(leaderboardDiv);

}

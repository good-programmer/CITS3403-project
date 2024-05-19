let debounce = false;
let follow;
let data;
let userid;
const createdPostTemplate = document.querySelector(".created-feed-template")
const ratedPostTemplate = document.querySelector(".rated-feed-template")
window.addEventListener('load', async function() {
    if (createdPostTemplate && ratedPostTemplate){
        await createUserFeed()
    }
    follow = document.getElementById("follow-button");
    data = await getUserData();
    if (follow) {
        userid = follow.dataset.targetuser;
        follow.addEventListener('click', postFollow);
    }
    //console.log(data);
    let sortCreatedSelect = document.getElementById('created-puzzles-sort');
    sortCreated(sortCreatedSelect.value, data['puzzles'])
    sortCreatedSelect.onchange = function() {sortCreated(sortCreatedSelect.value, data['puzzles']);}

    let sortCompletedSelect = document.getElementById('completed-puzzles-sort');
    sortCompleted(sortCompletedSelect.value, data['scores'])
    sortCompletedSelect.onchange = function() {sortCompleted(sortCompletedSelect.value, data['scores']);}

    let sortRatedSelect = document.getElementById('rated-puzzles-sort');
    sortRated(sortRatedSelect.value, data['ratings'])
    sortRatedSelect.onchange = function() {sortRated(sortRatedSelect.value, data['ratings']);}
});

function formatDate(date) {
    let now = new Date();
    let secs = (now.getTime() - date.getTime()) / 1000;
    //console.log(secs)
    let mins = secs / 60
    let hours = mins / 60;
    let days = hours / 24;
    let weeks = days / 7;
    let months = weeks / 4.35;
    let years = months / 12;
    if (secs < 90) {
        return Math.floor(secs) + ' seconds ago'
    }
    if (mins < 60) {
        return Math.floor(mins) + ' minutes ago'
    }
    if (hours < 24) {
        return Math.floor(hours) + ' hours ago'
    }
    if (days < 14) {
        return Math.floor(days) + ' days ago'
    }
    if (weeks < 5) {
        return Math.floor(weeks) + ' weeks ago'
    }
    if (months < 12) {
        return Math.floor(months) + ' months ago'
    }
    return Math.floor(years) + ' years ago'

    /*const year = date.getFullYear().toString().padStart(4,'0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return year + '-' + month + '-' + day;*/
}

async function createUserFeed() {
    const feedContainer = document.getElementById("feed-container")
    fetch('/user/feed')
    .then(response => response.json())
    .then(data => {
        data.slice().reverse().forEach(post => {
            if (post.type == 'created'){
                //console.log("entered")
                const createdPost = createdPostTemplate.content.cloneNode(true)
                const puzzle = createdPost.querySelector(".followed-creator-puzzle-title")
                const followed = createdPost.querySelector(".followed-creator-name")
                const date = createdPost.querySelector(".followed-date-created")
                const dateAsDate = new Date(post.date)

                puzzle.textContent = post.title
                puzzle.href = '/puzzle/'+String(post.id)+'/info'

                followed.textContent = post.followed
                followed.href = '/user/'+String(post.followedID)+'/profile'

                date.textContent = formatDate(dateAsDate)

                feedContainer.append(createdPost)
            }
            if (post.type == 'rated'){
                //console.log("entered")
                const ratedPost = ratedPostTemplate.content.cloneNode(true)
                const puzzle = ratedPost.querySelector(".followed-creator-puzzle-title")
                const followed = ratedPost.querySelector(".followed-name")
                const date = ratedPost.querySelector(".followed-date-rated")
                const rating = ratedPost.querySelector(".followed-given-rating")
                const dateAsDate = new Date(post.date)

                puzzle.textContent = post.title
                puzzle.href = '/puzzle/'+String(post.id)+'/info'

                followed.textContent = post.followed
                followed.href = '/user/'+String(post.followedID)+'/profile'

                date.textContent = formatDate(dateAsDate)

                rating.textContent = post.rated.toFixed(1);

                feedContainer.append(ratedPost)
            }
        })

    })
}

async function getUserData() {
    let userid = window.location.pathname.split('/')[2];
    //console.log(userid)
    const response = await fetch('/user/' + userid);
    const data = await response.json();
    return data;
}

function createPostBody(puzzle) {
    let puzzleUrl = '/puzzle/' + puzzle['id'] + '/info';
    let userUrl = '/user/' + puzzle['creatorID'] + '/profile';
    let el = document.createElement('div');
    el.className = 'post-body';

    let puzzleLink = document.createElement('a');
    puzzleLink.href = puzzleUrl;
    puzzleLink.innerHTML = `<b>${puzzle['title']}</b>`;
    puzzleLink.className = 'matrix-puzzle';
    puzzleLink.onmouseover = function() {
        this.classList.add('matrix-puzzle');
    };
    puzzleLink.onmouseout = function() {
        this.classList.remove('matrix-puzzle');
    };

    let creatorLink = document.createElement('a');
    creatorLink.href = userUrl;
    creatorLink.className = 'matrix-user';
    creatorLink.innerHTML = puzzle['creator'];

    el.appendChild(puzzleLink);
    el.appendChild(document.createElement('br'));
    el.appendChild(creatorLink);
    el.appendChild(document.createElement('br'));

    return el;
}


function sortCreated(order, lst) {
    let list = [...lst];
    let createdList = document.getElementById('created-list');
    createdList.innerHTML = ''
    if (order == 'play_count') {
        list.sort(function (a, b) {
            if (a['play_count'] > b['play_count']) return -1; else return 1;
        })
    } else {
        list.sort(function (a, b) {
            if (a['average_rating'] > b['average_rating']) return -1; else return 1;
        })
    }
    for (puzzle of list) {
        let el = createPostBody(puzzle);
        el.innerHTML = el.innerHTML + 
                        `Total plays: <span class="matrix-number">${puzzle['play_count']}</span><br>
                        Average rating: <span class="matrix-number">${puzzle['average_rating'].toFixed(2)}</span><br>
                        Highest score: <span class="matrix-number">${puzzle['highscore']}</span>`;
        createdList.appendChild(el);
    }

    if (list.length == 0) {createdList.dataset.empty = true;}
}

function sortCompleted(order, lst) {
    let list = [...lst];
    let completedList = document.getElementById('completed-list');
    completedList.innerHTML = ''
    if (order == 'score') {
        list.sort(function (a, b) {
            if (a['score'] > b['score']) return -1; else return 1;
        })
    } else {
        list.sort(function (a, b) {
            if (a['dateSubmitted'] > b['dateSubmitted']) return -1; else return 1;
        })
    }
    for (puzzle of list) {
        let el = createPostBody(puzzle);
        el.innerHTML = el.innerHTML + 
                        `Total plays: <span class="matrix-number">${puzzle['play_count']}</span><br>
                        Score: <span class="matrix-number">${puzzle['score']}</span><br>
                        Date completed: <span class="matrix-number">${puzzle['dateSubmitted'].slice(0,10)}</span>`;
        completedList.appendChild(el);
    }

    if (list.length == 0) {completedList.dataset.empty = true;}
}

function sortRated(order, lst) {
    let list = [...lst];
    let ratedList = document.getElementById('rated-list');
    ratedList.innerHTML = ''
    if (order == 'rating') {
        list.sort(function (a, b) {
            if (a['rating'] > b['rating']) return -1; else return 1;
        })
    } else {
        list.sort(function (a, b) {
            if (a['dateRated'] > b['dateRated']) return -1; else return 1;
        })
    }
    for (puzzle of list) {
        let el = createPostBody(puzzle);
        el.innerHTML = el.innerHTML + 
                        `Total plays: <span class="matrix-number">${puzzle['play_count']}</span><br>
                        Rating: <span class="matrix-number">${puzzle['rating'].toFixed(1)}</span><br>
                        Date rated: <span class="matrix-number">${puzzle['dateRated'].slice(0,10)}</span>`;
        ratedList.appendChild(el);
    }

    if (list.length == 0) {ratedList.dataset.empty = true;}
}

async function postFollow() {
    if (debounce) return;
    debounce = true;
    let action = '/user/' + follow.dataset.targetaction;
    const response = await fetch(action, {
        method: "POST",
        mode: "same-origin",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {"Content-Type": "application/json"},
        redirect: "error",
        body: JSON.stringify({"id": parseInt(userid)}),
        });
    if (response.status === 200) {
        if (follow.dataset.targetaction === 'follow') {
            follow.dataset.targetaction = 'unfollow';
            follow.textContent = '[UNFOLLOW]';
        } else {
            follow.dataset.targetaction = 'follow';
            follow.textContent = '[FOLLOW]';
        }
    }
    debounce=false;
};
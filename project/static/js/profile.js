let debounce = false;
let follow;
let data;
let userid;
window.onload = async function() {
    follow = document.getElementById("follow-button");
    data = await getUserData();
    if (follow) {
        userid = follow.dataset.targetuser;
        follow.addEventListener('click', postFollow);
    }
    console.log(data);
    let sortCreatedSelect = document.getElementById('created-puzzles-sort');
    sortCreated(sortCreatedSelect.value, data['puzzles'])
    sortCreatedSelect.onchange = function() {sortCreated(sortCreatedSelect.value, data['puzzles']);}

    let sortCompletedSelect = document.getElementById('completed-puzzles-sort');
    sortCompleted(sortCompletedSelect.value, data['scores'])
    sortCompletedSelect.onchange = function() {sortCompleted(sortCompletedSelect.value, data['scores']);}

    let sortRatedSelect = document.getElementById('rated-puzzles-sort');
    sortRated(sortRatedSelect.value, data['ratings'])
    sortRatedSelect.onchange = function() {sortRated(sortRatedSelect.value, data['ratings']);}
}

async function getUserData() {
    let userid = window.location.pathname.split('/')[2];
    console.log(userid)
    const response = await fetch('/user/' + userid);
    const data = await response.json();
    return data;
}

function createPostBody(puzzle) {
    let puzzleUrl = '/puzzle/'+puzzle['id'] + '/info';
    let userUrl = '/user/'+puzzle['creatorID'] + '/profile';
    let el = document.createElement('div');
    el.className = 'post-body';
    el.innerHTML = `<a href=${puzzleUrl}><b>${puzzle['title']}</b></a><br>
                    <a href=${userUrl}>${puzzle['creator']}</a><br>`
    return el
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
                        `Total plays: ${puzzle['play_count']}<br>
                        Average rating: ${puzzle['average_rating'].toFixed(2)}<br>
                        Highest score: ${puzzle['highscore']}`;
        createdList.appendChild(el);
    }
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
                        `Total plays: ${puzzle['play_count']}<br>
                        Score: ${puzzle['score']}<br>
                        Date completed: ${puzzle['dateSubmitted'].slice(0,10)}`;
        completedList.appendChild(el);
    }
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
                        `Total plays: ${puzzle['play_count']}<br>
                        Rating: ${puzzle['rating'].toFixed(1)}<br>
                        Date rated: ${puzzle['dateRated'].slice(0,10)}`;
        ratedList.appendChild(el);
    }
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
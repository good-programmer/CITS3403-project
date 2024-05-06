window.onload = async function() {
    let puzzleid = window.location.pathname.split('/')[2]
    let switchLeaderboard = document.getElementById("switch-leaderboard-button");
    let main = document.getElementById("main-leaderboard");
    let following = document.getElementById("following-leaderboard");
    switchLeaderboard.onclick = function() {
        if (main.style.display == "none") {
            switchLeaderboard.textContent = "All";
            main.style.display = "block";
            following.style.display = "none";
        } else {
            switchLeaderboard.textContent = "Following";
            main.style.display = "none";
            following.style.display = "block";
        }
    }

    let storedRating = 0;
    let currentRating = 0;
    let rateSlider = document.getElementById('rate-slider');
    let x = rateSlider.getBoundingClientRect().left
    let w = document.getElementById('rate-back').getBoundingClientRect().right - x
    rateSlider.addEventListener('mousemove',function(e) {
        let offset = (e.x - x) / w;
        offset = Math.round(offset * 10) / 10 * w
        document.getElementById('rate-current').setAttribute('style','width:'+offset+'px');
        currentRating = Math.min(5, Math.max(0, offset / w * 5));

    })
    function resetRating(e) {
        document.getElementById('rate-current').setAttribute('style','width:'+ storedRating / 5 * w+'px');
    }
    rateSlider.addEventListener('mouseleave', resetRating);

    let response = await fetch("/puzzle/" + puzzleid);
    let puzzleInfo = await response.json();
    storedRating = 'rated' in puzzleInfo ? puzzleInfo['rated']['rating'] : 0
    resetRating();
    console.log(puzzleInfo);

}
window.onload = function() {
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
}
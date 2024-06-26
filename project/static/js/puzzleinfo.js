document.querySelectorAll(".toggle-button").forEach(togBut => {
    togBut.addEventListener("click", () => {
        let main = document.getElementById("main-leaderboard");
        let following = document.getElementById("following-leaderboard");

        document.querySelectorAll(".toggle-button").forEach(otherBut => {
            otherBut.classList.remove("toggle-button--selected");
        });

        togBut.classList.add("toggle-button--selected");

        if (!following) return;

        if (togBut.textContent.trim().toLowerCase() == "all") {
            main.setAttribute("data-display", "true");
            following.setAttribute("data-display", "false");
        } else {
            main.setAttribute("data-display", "false");
            following.setAttribute("data-display", "true");
        }
    });
});
document.querySelector(".toggle-button").click();



window.onload = async function() {
    let puzzleid = window.location.pathname.split('/')[2]

    let response = await fetch("/puzzle/" + puzzleid);
    let puzzleInfo = await response.json();

    let playButton = document.getElementById("play-button");

    if (!playButton.getAttribute('disabled')) {
        playButton.addEventListener('click', function() {window.location.href = playButton.dataset.href;})
    }

    let storedRating = 'rated' in puzzleInfo ? puzzleInfo['rated']['rating'] : 0
    let rateSlider = document.getElementById('rate-slider');
    let x = rateSlider.getBoundingClientRect().left
    let w = document.getElementById('rate-back').getBoundingClientRect().right - x

    function resetRating(e) {
        document.getElementById('rate-current').setAttribute('style','width:'+ storedRating / 5 * w+'px');
    }
    rateSlider.addEventListener('mouseleave', resetRating);
    resetRating();

    if ('score' in puzzleInfo) {
        let currentRating = 0;
        rateSlider.addEventListener('mousemove',function(e) {
            let offset = (e.x - x) / w;
            offset = Math.round(offset * 10) / 10 * w
            offset = Math.min(w, Math.max(0, offset));
            document.getElementById('rate-current').setAttribute('style','width:'+offset+'px');
            currentRating = Math.min(5, Math.max(0, offset / w * 5));

        })

        let debounce = false;
        rateSlider.addEventListener('click', async function(){
            if (debounce) return;
            debounce = true;
            let rating = currentRating;
            let action = '/puzzle/' + puzzleid + '/rate';
            const response = await fetch(action, {
                method: "POST",
                mode: "same-origin",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {"Content-Type": "application/json"},
                redirect: "error",
                body: JSON.stringify({"rating": parseFloat(rating)}),
                });
            if (response.status === 200) {
                storedRating = rating;
                resetRating();
            }
            debounce=false;
        });
    } else {
        rateSlider.classList += 'disabled';
    }
}
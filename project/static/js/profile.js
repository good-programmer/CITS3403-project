window.onload = function() {
    let debounce = false;
    let follow = document.getElementById("follow-button");
    let userid = follow.dataset.targetuser;
    follow.addEventListener('click', async function() {
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
                follow.textContent = 'Unfollow';
            } else {
                follow.dataset.targetaction = 'follow';
                follow.textContent = 'Follow';
            }
        }
        debounce=false;
    });
}
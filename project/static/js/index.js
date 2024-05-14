const postTemplate = document.querySelector("[post-template]")
const postContainer = document.querySelector("[data-post-container]")

document.querySelectorAll(".toggle-button").forEach(togBut=>{
    togBut.addEventListener("click", () => {
    
        togBut.classList.toggle("toggle-button--selected")

        clearTemplates()

        sortBy = togBut.textContent.trim().toLowerCase()
        if(['recent','hot','popular'].includes(sortBy)){
            loadTemplates(sortBy)
        }

        document.querySelectorAll(".toggle-button").forEach(otherBut => {
            if (otherBut !== togBut) {
                otherBut.classList.remove("toggle-button--selected")
            }
        })
    })
    loadTemplates('recent')
})

function clearTemplates() {
    while (postContainer.firstChild) {
        postContainer.removeChild(postContainer.firstChild)
    }
}

function loadTemplates(trend){

    fetch('/puzzle/find/' + trend)
    .then(response => response.json())
    .then(data => {
        data.puzzles.forEach(puz => {
            const post = postTemplate.content.cloneNode(true)

            const puzTitle = post.querySelector("[data-puz-title]")
            puzTitle.textContent = puz.title
            puzTitle.href = '/puzzle/'+String(puz.id)+'/play'

            const puzID = post.querySelector("[data-puz-id]")
            puzID.textContent = puz.id
            puzID.href = '/puzzle/'+String(puz.id)+'/play'

            const authName = post.querySelector("[data-author-name]")
            authName.textContent = puz.creator
            authName.href = '/user/'+String(puz.creatorID)+'/profile'

            const authID = post.querySelector("[data-author-id]")
            authID.textContent = puz.creatorID
            authID.href = '/user/'+String(puz.creatorID)+'/profile'

            const dateCreation = post.querySelector("[data-date-created]")
            dateCreation.textContent = puz.dateCreated.slice(0,10)

            const playcount = post.querySelector("[data-playcount]")
            playcount.textContent = puz.play_count

            const avgRating= post.querySelector("[data-avg-rating]")
            avgRating.textContent = puz.average_rating.toFixed(1)

            const highestScore = post.querySelector("[data-highscore]")
            highestScore.textContent = puz.highscore

            postContainer.append(post)
        });
    })
    .catch(error => console.error('Error fetching data:', error));

}
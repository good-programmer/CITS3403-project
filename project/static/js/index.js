const postTemplate = document.querySelector("[post-template]")
const postContainer = document.querySelector("[data-post-container]")

fetch('/puzzle/search/recent')
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
            dateCreation.textContent = puz.dateCreated

            const playcount = post.querySelector("[data-playcount]")
            playcount.textContent = puz.play_count

            const avgRating= post.querySelector("[data-avg-rating]")
            avgRating.textContent = puz.average_rating

            const highestScore = post.querySelector("[data-highscore]")
            highestScore.textContent = puz.highscore

            postContainer.append(post)
        });
    })
    .catch(error => console.error('Error fetching data:', error));



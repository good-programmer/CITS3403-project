const postTemplate = document.querySelector(".post-template")
const postContainer = document.querySelector("[data-post-container]")
const pageNumContainer = document.getElementById("page-num-container")
const pageNumTemplate = document.querySelector(".page-num-template")
const nextButton = document.getElementById("right-arrow")
const prevButton = document.getElementById("left-arrow")
let currentParams =  new URLSearchParams(window.location.search)
nextButton.disabled = true;
prevButton.disabled = true;
let totalPages = 1;
let currentPage = 1
let sortBy = 'recent';

if (window.location.pathname === '/'){
    loadTemplates('/recent');
}

document.querySelectorAll(".toggle-button").forEach(togBut=>{
    togBut.addEventListener("click", () => {
    
        togBut.classList.toggle("toggle-button--selected", true)

        sortBy = togBut.textContent.trim().toLowerCase()
        if(['recent','hot','popular'].includes(sortBy)){
            clearTemplates()
            const newURL = '/' + sortBy + '?page=1'
            currentPage = 1;
            loadTemplates(newURL)
            if (window.location.pathname.includes('search')) {
                window.history.pushState({}, null, newURL);
            }
        }

        document.querySelectorAll(".toggle-button").forEach(otherBut => {
            if (otherBut !== togBut) {
                otherBut.classList.remove("toggle-button--selected")
            }
        })
    })
})

function clearTemplates() {
    while (postContainer.firstChild) {
        postContainer.removeChild(postContainer.firstChild)
    }
    while (pageNumContainer.firstChild) {
        pageNumContainer.removeChild(pageNumContainer.firstChild)
    }
}

function loadTemplates(trend){
    nextButton.disabled = true;
    prevButton.disabled = true;
    postContainer.dataset.empty = false;
    postContainer.dataset.loading = true;
    fetch('/puzzle/find' + trend)
    .then(response => response.json())
    .then(data => {
        postContainer.dataset.loading = false;
        postContainer.dataset.empty = (data.puzzles.length === 0);
        data.puzzles.forEach(puz => {
            const post = postTemplate.content.cloneNode(true)

            const puzTitle = post.querySelector("[data-puz-title]")
            puzTitle.textContent = puz.title
            puzTitle.href = '/puzzle/'+String(puz.id)+'/play'

            const puzID = post.querySelector("[data-puz-id]")
            puzID.textContent = puz.id
            puzID.href = '/puzzle/'+String(puz.id)+'/info'

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
        })
        const url = new URL(window.location.href);
        const params = new URLSearchParams(url.search);
        totalPages = data.pages;
        updatePageNumDisplay();
    })
    .catch(error => console.error('Error fetching data:', error));
}

function updatePageNumDisplay(){
    currentParams = new URLSearchParams(window.location.search)
    //currentPage = parseInt(currentParams.get('page'))
    for (let i = 1; i <= parseInt(totalPages); i++){
        const pageNumButtonTemp = pageNumTemplate.content.cloneNode(true)
        const pageNumButton = pageNumButtonTemp.querySelector("[data-pnButton]")
        pageNumButton.textContent = i
        //console.log(i, currentPage)
        if (i === currentPage){
            
            //console.log("this is what i see: " + currentPage)
            pageNumButton.classList.toggle("current-page")
        }
        const totalShowing = 6
        let rightShowing = 4
        let leftShowing = 1
        if (currentPage === 1) {
            rightShowing = 5
            leftShowing = 1
        }
        if ((currentPage + 4)>=totalPages){
            rightShowing = totalPages - currentPage
            leftShowing = totalShowing - 1 - rightShowing
        }
        if ((i > (currentPage + rightShowing)) || (i < (currentPage - leftShowing))){
            pageNumButton.disabled = true
        }
        pageNumButton.onclick = () => goToPage(i);
        pageNumContainer.appendChild(pageNumButton)
    }
    prevButton.disabled = currentPage === 1 || totalPages == 0;
    nextButton.disabled = currentPage === totalPages || totalPages == 0;
}
function goToPage(page) {
    currentPage = page;
    clearTemplates()
    const newURL = '/' + sortBy + '?page=' + currentPage
    loadTemplates(newURL);
    if (window.location.pathname.includes('search')) {
        window.history.pushState({}, null, newURL);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        goToPage(currentPage + 1);
    }
}

function previousPage() {
    if (currentPage > 1) {
        goToPage(currentPage - 1);
    }
}

nextButton.addEventListener("click", ()=>{goToPage(currentPage + 1)})
prevButton.addEventListener("click", ()=>{goToPage(currentPage - 1)})
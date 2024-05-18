//url map preparation
const searchMap = new Map()
const defaultMap = new Map()
const storedMap = new Map()

let pageSize = 10

let currentURL = ''

defaultMap.set('page', '1');
defaultMap.set('page_size', '10')
defaultMap.set('query', '');
defaultMap.set('rating', '0-5');
defaultMap.set('after', '0000-01-01')
defaultMap.set('to', '9999-01-01')
defaultMap.set('completed', 'any');
defaultMap.set('play_count', '0-999999');
defaultMap.set('sort_by', 'date');
defaultMap.set('order', 'desc');
defaultMap.set('following', 'false');

storedMap.set('rating', '0-5');
storedMap.set('after', '0000-01-01')
storedMap.set('to', '9999-01-01')
storedMap.set('play_count', '0-999999');

function setDefault (keyName){
    searchMap.set(keyName, defaultMap.get(keyName))
}


const keyNameList = ['page', 'page_size', 'query', 'rating', 'after', 'to', 'completed', 'play_count', 'following', 'sort_by', 'order']

function handleSubmit(){
    let urlInjection ='?'
    for (const keyName of keyNameList){
        if (searchMap.get(keyName)==defaultMap.get(keyName)) {
            if (keyName == 'page'){
                urlInjection += "&page=1"
            }
            continue
        }
        urlInjection += '&' + keyName + '=' + searchMap.get(keyName)
    }
    clearTemplates()
    window.history.pushState({}, null, urlInjection)
    loadTemplates(urlInjection)
}

function updatePageForSize(){
    searchMap.set('page', '1')
    searchMap.set('page_size', pageSize)
    handleSubmit()
}

goToPage = function (page) {
    currentPage = page
    searchMap.set('page', currentPage)
    handleSubmit()
}

//event listeners for rating
const minRating = document.getElementById('min-rating');
const maxRating = document.getElementById('max-rating');
minRating.addEventListener('change', function() {
    const currentMinValue = parseInt(minRating.value);
    const previousMaxValue = maxRating.value;

    maxRating.innerHTML = '';

    const optionElement = document.createElement('option');
    optionElement.textContent = 'Maximum Rating:';
    optionElement.value = 5;
    maxRating.appendChild(optionElement);

    for (let i = currentMinValue; i <= 5; i++) {
        const optionElement = document.createElement('option');
        optionElement.textContent = i;
        optionElement.value = i;
        maxRating.appendChild(optionElement);
    }
    if (parseInt(previousMaxValue) >= currentMinValue) {
        maxRating.value = previousMaxValue;
    }
    const newValue = String(minRating.value) + '-' + String(maxRating.value)
    searchMap.set('rating', newValue)
    console.log(searchMap.get('rating')) 
});
maxRating.addEventListener('change', function() {
    const previousMinValue = minRating.value;
    const currentMaxValue = parseInt(maxRating.value);

    minRating.innerHTML = '';
    const optionElement = document.createElement('option');
    optionElement.textContent = 'Minimum Rating:';
    optionElement.value = 0;
    minRating.appendChild(optionElement);

    for (let i = 0; i <= currentMaxValue; i++) {
        const optionElement = document.createElement('option');
        optionElement.textContent = i;
        optionElement.value = i;
        minRating.appendChild(optionElement);
    }
    if (parseInt(previousMinValue) <= currentMaxValue) {
        minRating.value = previousMinValue;
    }
    const newValue = String(minRating.value) + '-' + String(maxRating.value)
    searchMap.set('rating', newValue)
    console.log(searchMap.get('rating'))
})

//event listeners for button labels
function toggleRowLabel (isOn, browseClass){
    const elmnts = document.querySelectorAll(browseClass)
    const labels = document.querySelectorAll(browseClass + '-label')
    elmnts.forEach(elmnt =>{
        elmnt.style['display'] = isOn ? 'block' : 'none'
    })
    labels.forEach(label =>{
        label.style['display'] = isOn ? 'block' : 'none'
    })
}
function handleDate(isOn){
    if (!isOn){
        storedMap.set('after', searchMap.get('after'))
        storedMap.set('to', searchMap.get('to'))
        setDefault('after')
        setDefault('to')
    }
    else{
        searchMap.set('after', storedMap.get('after'))
        searchMap.set('to', storedMap.get('to'))
    }
}
document.querySelectorAll(".row-label").forEach(rowLabel=>{
    rowLabel.addEventListener("click", () => {
        rowLabel.classList.toggle("row-label--selected")
        const isOn = rowLabel.classList.contains('row-label--selected');
        const keyName = rowLabel.textContent.replace(" ","_")
        
        if (keyName == 'date'){
            handleDate(isOn)
        }
        else if (!isOn){
            storedMap.set(keyName, searchMap.get(keyName))
            setDefault(keyName)
        }
        else{
            searchMap.set(keyName, storedMap.get(keyName))
        }

        const className = '.' + keyName
        toggleRowLabel(isOn, className)
        if (keyName == 'date'){
            console.log(searchMap.get('after'))
            console.log(searchMap.get('to'))
        }
        else{
            console.log(searchMap.get(keyName))
        }
    })
})

//event listeners for page size
const pageSizeMenu = document.getElementById("page-size")
pageSizeMenu.addEventListener("change", function(){
    pageSize = pageSizeMenu.value
    updatePageForSize()
})

//event listerners for page number
const pageNumDisplay = document.getElementById("page-select")
const leftArrow = document.getElementById("left-arrow")
const rightArrow = document.getElementById("right-arrow")
//event listeners for playcount
document.querySelectorAll(".play_count").forEach(numInput=>{
    numInput.addEventListener('input', function(){
        const inputVal = numInput.value
        if (inputVal > 999999) {numInput.value = 999999}
        numInput.value = inputVal.replace(/[^0-9]/g, '')
    })
})
const minPlaycount = document.getElementById("min-playcount")
const maxPlaycount = document.getElementById("max-playcount")
minPlaycount.addEventListener('blur', function(){
    const minimumCount = parseFloat(minPlaycount.value)
    const maximumCount = parseFloat(maxPlaycount.value)

    if(minimumCount > maximumCount){
        minPlaycount.value = maximumCount - 1
    }

    const newValue = String(minPlaycount.value) + '-' + String(maxPlaycount.value)
    searchMap.set('play_count', newValue)
    console.log(searchMap.get('play_count'))
})
maxPlaycount.addEventListener('blur', function(){
    const minimumCount = parseFloat(minPlaycount.value)
    const maximumCount = parseFloat(maxPlaycount.value)

    if(minimumCount > maximumCount){
        maxPlaycount.value = minimumCount + 1
    }

    const newValue = String(minPlaycount.value) + '-' + String(maxPlaycount.value)
    searchMap.set('play_count', newValue)
    console.log(searchMap.get('play_count'))
})
//event listeners for date
function formatDate(date) {
    const year = date.getFullYear().toString().padStart(4,'0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return year + '-' + month + '-' + day;
}
const minDate = document.getElementById('min-date');
const maxDate = document.getElementById('max-date');
minDate.addEventListener('input', function() {
    const minDateVal = new Date(minDate.value);
    const maxDateVal = new Date(maxDate.value);

    if (!maxDate.value) {maxDateVal.setFullYear(9999, 0, 1)}
    if (!minDate.value) {minDateVal.setFullYear(0, 0, 1)}

    if (maxDateVal < minDateVal) {
        maxDate.valueAsDate = minDateVal;
    }

    searchMap.set('after', formatDate(minDateVal))
    searchMap.set('to', formatDate(maxDateVal))
    console.log(searchMap.get('after'))
    console.log(searchMap.get('to'))
});
maxDate.addEventListener('input', function() {
    const minDateVal = new Date(minDate.value);
    const maxDateVal = new Date(maxDate.value);

    if (!maxDate.value) {maxDateVal.setFullYear(9999, 0, 1)}
    if (!minDate.value) {minDateVal.setFullYear(0, 0, 1)}

    if (maxDateVal < minDateVal) {
        minDate.valueAsDate = maxDateVal;
    }

    searchMap.set('after', formatDate(minDateVal))
    searchMap.set('to', formatDate(maxDateVal))
    console.log(searchMap.get('after'))
    console.log(searchMap.get('to'))
});

//event listers for basic-toggle
document.querySelectorAll(".basic-toggle").forEach(basicToggle=>{
    basicToggle.addEventListener("click", () => {
        basicToggle.classList.toggle("basic-toggle--selected")
    })
})
//event listener for order
const orderButton = document.getElementById("order")
orderButton.addEventListener("click", () =>{
    const isDesc = orderButton.classList.contains('basic-toggle--selected');
    if (isDesc){
        orderButton.textContent = 'Descending'
        searchMap.set('order', 'desc')
    }
    else{
        orderButton.textContent = 'Ascending'
        searchMap.set('order', 'asc')
    }
    console.log(searchMap.get('order'))
})

let currentCompletedState = 'any';
const ignoreCompleted = document.getElementById("ignore-completed")
ignoreCompleted.addEventListener("click", () =>{
    if (currentCompletedState === 'any') {
        ignoreCompleted.classList.add("basic-toggle--selected");
        currentCompletedState = 'false';
    } else {
        if (currentCompletedState === 'false') {
            currentCompletedState = 'true';
            ignoreCompleted.textContent = 'Show completed';
        } else {
            currentCompletedState = 'any';
            ignoreCompleted.textContent = 'Ignore completed';
            ignoreCompleted.classList.remove("basic-toggle--selected");
        }
    }
    searchMap.set('completed', currentCompletedState);
})

//event listener for following
const followButton = document.getElementById("filter-following");
followButton.addEventListener("click", () =>{
    const follow = followButton.classList.contains('basic-toggle--selected');
    if (follow){
        console.log('set to true');
        searchMap.set('following', 'true')
    }
    else{
        searchMap.set('following', 'false')
    }
})

//event listeners for search
const searchInput = document.getElementById("search")
const submitButton = document.getElementById("submit-search")
searchInput.addEventListener("input", e =>{
    const input = e.target.value
    searchMap.set('query', input)
    console.log(searchMap.get("query"))
})
searchInput.addEventListener("keypress", function(event){
    if (event.key === 'Enter'){
        setDefault('page')
        currentPage = 1
        handleSubmit()
    }
})
submitButton.addEventListener("click", function(){
    setDefault('page')
    currentPage = 1
    handleSubmit()
}
)

function updateSearchWithParams() {
    let currentParams = new URLSearchParams(window.location.search);
    for (const keyName of keyNameList){
        if (currentParams.get(keyName) === null) {
            setDefault(keyName)
        } else {
            searchMap.set(keyName, currentParams.get(keyName));
        }
    }
    if (currentParams.size > 0){
        handleSubmit()
    } else {
        loadTemplates('/recent');
    }
}

window.addEventListener('popstate', function () {
    console.log('history changed');
    updateSearchWithParams();
})

updateSearchWithParams();

//event listeners for sort
document.querySelectorAll("#sort-filter-container .toggle-button").forEach(togBut=>{
    togBut.addEventListener("click", () => {
        sortBy = togBut.textContent.trim().toLowerCase().replace(' ', '_')
        
        if (sortBy == 'alphabet') {sortBy = 'a-z'}

        searchMap.set('sort_by', sortBy)

        console.log(searchMap.get('sort_by'))
    })
})


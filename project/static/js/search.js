//url map preparation
const searchMap = new Map()
const defaultMap = new Map()
const storedMap = new Map()

defaultMap.set('query', '');
defaultMap.set('rating', '0-5');
defaultMap.set('date', { after: '0000-01-01', to: '9999-01-01' });
defaultMap.set('completed', 'true');
defaultMap.set('play_count', '0-999999');
defaultMap.set('sort_by', 'date');
defaultMap.set('order', 'desc');

storedMap.set('rating', '0-5');
storedMap.set('date', { after: '0000-01-01', to: '9999-01-01' });
storedMap.set('play_count', '0-999999');

function setDefault (keyName){
    searchMap.set(keyName, defaultMap.get(keyName))
}

const keyNameList = ['query', 'rating', 'date', 'completed', 'play_count', 'sort_by', 'order']
for (const keyName of keyNameList){
    setDefault(keyName)
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
document.querySelectorAll(".row-label").forEach(rowLabel=>{
    rowLabel.addEventListener("click", () => {
        rowLabel.classList.toggle("row-label--selected")
        const isOn = rowLabel.classList.contains('row-label--selected');
        const keyName = rowLabel.textContent.replace(" ","_")

        if (!isOn){
            storedMap.set(keyName, searchMap.get(keyName))
            setDefault(keyName)
        }
        else{
            searchMap.set(keyName, storedMap.get(keyName))
        }

        const className = '.' + keyName
        toggleRowLabel(isOn, className)
        console.log(searchMap.get(keyName))
    })
})

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

    searchMap.set('date', { after: formatDate(minDateVal), to: formatDate(maxDateVal) })
    console.log(searchMap.get('date'))
});
maxDate.addEventListener('input', function() {
    const minDateVal = new Date(minDate.value);
    const maxDateVal = new Date(maxDate.value);

    if (!maxDate.value) {maxDateVal.setFullYear(9999, 0, 1)}
    if (!minDate.value) {minDateVal.setFullYear(0, 0, 1)}

    if (maxDateVal < minDateVal) {
        minDate.valueAsDate = maxDateVal;
    }
    searchMap.set('date', { after: formatDate(minDateVal), to: formatDate(maxDateVal) })
    console.log(searchMap.get('date'))
});

//event listers for basic-toggle
document.querySelectorAll(".basic-toggle").forEach(basicToggle=>{
    basicToggle.addEventListener("click", () => {
        basicToggle.classList.toggle("basic-toggle--selected")
    })
})

const orderButton = document.getElementById("order")
orderButton.addEventListener("click", () =>{
    const isDesc = orderButton.classList.contains('basic-toggle--selected');
    orderButton.textContent = isDesc ? 'Descending' : 'Ascending'
})

//event listiners for search
const searchSubmit = document.getElementById("search-trigger")
const searchInput = document.getElementById("search")
searchInput.addEventListener("input", e =>{
    const input = e.target.value
    searchMap.set('query', input)
    console.log(searchMap.get("query"))
})
searchSubmit.addEventListener("submit", () =>{
    const query = searchInput.value.lower.trim
})
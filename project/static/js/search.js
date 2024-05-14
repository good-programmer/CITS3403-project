const minRating = document.getElementById('min-rating');
const maxRating = document.getElementById('max-rating');

//event listeners for rating
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
})


//event listeners for button labels
function toggleRowLabel (isOn, browseClass, rowLabel){
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
        const className = '.' + rowLabel.textContent
        toggleRowLabel(isOn, className, rowLabel)
    })
})

//event listeners for playcount
document.querySelectorAll(".playcount").forEach(numInput=>{
    numInput.addEventListener('input', function(){
        const inputVal = numInput.value
        if (inputVal > Number.MAX_SAFE_INTEGER) {numInput.value = Number.MAX_SAFE_INTEGER}
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
})
maxPlaycount.addEventListener('blur', function(){
    const minimumCount = parseFloat(minPlaycount.value)
    const maximumCount = parseFloat(maxPlaycount.value)

    if(minimumCount > maximumCount){
        maxPlaycount.value = minimumCount + 1
    }
})
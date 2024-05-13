const minRating = document.getElementById('min-rating');
const maxRating = document.getElementById('max-rating');

    // Event listener for menu1
    minRating.addEventListener('change', function() {
        const currentMinValue = parseInt(minRating.value);
        const previousMaxValue = maxRating.value;

        // Clear existing options in menu2
        maxRating.innerHTML = '';

        const optionElement = document.createElement('option');
        optionElement.textContent = 'Maximum Rating:';
        optionElement.value = 5;
        maxRating.appendChild(optionElement);

        // Add new options to menu2 based on selection of menu1
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

    // Event listener for menu2
    maxRating.addEventListener('change', function() {
        const previousMinValue = minRating.value;
        const currentMaxValue = parseInt(maxRating.value);

        minRating.innerHTML = '';
        const optionElement = document.createElement('option');
        optionElement.textContent = 'Minimum Rating:';
        optionElement.value = 0;
        minRating.appendChild(optionElement);
        // Add new options to menu2 based on selection of menu1
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

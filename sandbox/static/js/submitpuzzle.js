$(document).ready(function(){

  // Function to slide down the instructions information
  $("#showInstructions").click(function(){
      $("#instructions").slideDown("slow");
  });

  // Function to check input string for non-alphabetical characters
  function checkInput(input) {
      // Regex for special characters
      var alphaChars = /^[a-zA-Z]+$/;

      // Check if input contains only alphabetical characters
      if (!alphaChars.test(input)) {
          alert("String can only have alphabetical characters");
          return false;
      }
      
      // Check if input length for correctness
      strLen = input.length
      if (strLen > 10 || strLen < 3) {
          alert("String is incorrect length, string needs to be < 10 and > 2");
          return false;
      }

      // If input passes all checks, return true
      return true;
  }

  // Event listener for form submission
  $("form").submit(function(event){
      var inputValue = $("#puzzle").val();

      // Check the input value
      if (!checkInput(inputValue)) {
          // If input is invalid, prevent form submission
          event.preventDefault();
      }
  });
});

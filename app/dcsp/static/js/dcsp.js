/*
    Javascript for DCSP app
*/

function submitForm() {
    /*
      To use this functionality to display a spinner whilst the page is
      waiting to load the next page, use id="id_form" in your form tag and
      id="id_button" onclick="submitForm()" in your button. The button 
      will be disabled once pressed.
    */
    var form = document.getElementById('id_form');
    var submitBtn = document.getElementById('id_button');
    var loadingIcon = document.getElementById('loading-icon');

    loadingIcon.classList.add('show');
    submitBtn.disabled = true;

    setTimeout(function() {
      form.submit();
    }, 0);
}


function change_visibility() {
  var allElements = document.querySelectorAll('[id]');
  var installation_type = document.getElementById("id_setup_choice").value;
  var choice1 = "import"
  var choice2 = "start_anew"

  for (var i = 0; i < allElements.length; i++) {
      var element = allElements[i];
      
      if (element.id.includes(choice1) || element.id.includes(choice2)) {
          element.style.display = "none";
          element.required = false;
      }
  }

  if (installation_type === choice1) {
      for (var i = 0; i < allElements.length; i++) {
          var element = allElements[i];
          
          if (element.id.includes(choice1)) {
              element.style.display = "block";
              element.required = true;
          }
      }
  } 
  else if (installation_type === choice2) {
      for (var i = 0; i < allElements.length; i++) {
          var element = allElements[i];
          
          if (element.id.includes(choice2)) {
              element.style.display = "block";
              element.required = true;
          }
      }
  } 
};


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

    // Check if the form is valid
    if (!form.checkValidity()) {
        // The form is not valid, so don't submit it
        return;
    }

    save_button_pressed = true;

    loadingIcon.classList.add('show');
    submitBtn.disabled = true;
    
    form.submit();
};


function url_click(url) {
    const links = document.querySelectorAll('[id^="id_link"]');
    //var link = document.getElementById(link_id);
    var loadingIcon = document.getElementById('loading-icon');

    links.forEach(element => {
        element.style.pointerEvents = 'none'; // Disable the link
      });
    //link.style.pointerEvents = 'none'; // Disable the link
    loadingIcon.classList.add('show');

    window.location.href = url;
};


window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        const links = document.querySelectorAll('[id^="id_link"]');
        //var link = document.getElementById('id_link');
        var loadingIcon = document.getElementById('loading-icon');
        
        links.forEach(element => {
            element.style.pointerEvents = ''; // Enable link
          });

        //link.style.pointerEvents = ''; // Enable link
        loadingIcon.classList.remove('show');
    }
});


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


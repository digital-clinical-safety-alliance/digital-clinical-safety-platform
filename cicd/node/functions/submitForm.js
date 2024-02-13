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

    save_button_pressed = true;

    loadingIcon.classList.add('show');
    submitBtn.disabled = true;
    
    form.submit();
};
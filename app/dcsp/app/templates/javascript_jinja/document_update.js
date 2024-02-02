<script>
    function update_web_view() {
        var placeholders = {{ placeholders | safe }};
        var document_markdown = document.getElementById("id_document_markdown");
        var web_view = document.getElementById("id_web_view");
        var event = new Event("change");
        //var inputString = document_markdown.value
        var inputString = document_markdown.value.replace(/---[\s\S]*?---/, '');
        for (var key in placeholders) {
            {% verbatim %}
                var placeholder = "{{ " + key + " }}";
            {% endverbatim %}
            var value = "<span class='text-black'>" + placeholders[key] + "</span>";
            inputString = inputString.replaceAll(placeholder, value)
        }

        web_view.innerHTML = marked.parse(inputString);
        web_view.dispatchEvent(event);

        web_view.style.height = "auto";
        document_markdown.style.height = "auto";

        var web_viewHeight = web_view.scrollHeight;
        var document_markdownHeight = document_markdown.scrollHeight;

        var maxHeight = Math.max(web_viewHeight, document_markdownHeight);
        web_view.style.height = maxHeight + "px";
        document_markdown.style.height = maxHeight + "px";
    };


    var save_button_pressed = false;

    window.addEventListener('beforeunload', function(event) {
        const value_new = document.getElementById('id_document_markdown').value;
        const value_old = document.getElementById('id_document_markdown_initial').value;

        if (value_new !== value_old && save_button_pressed === false){
            event.returnValue = "You have unsaved changes. Are you sure you want to leave?";
            // TODO #52 - need to find out how to remove loading icon if user does not leave page
        }
    });
</script>

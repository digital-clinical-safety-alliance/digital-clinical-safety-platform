<script>
    var labelsForCalculations = {{ form.labels_for_calculations|safe }};
    var calculationField = {{ form.calculation_field|safe }};


    function handleFieldChange(event) {
      var calculationKey = {};
      var searchKey = "";
      var calculation_output = "";

      for (var key in labelsForCalculations) {
        var changedValue = document.getElementById(key).value.split("{{ MKDOCS_TEMPLATE_NUMBER_DELIMITER }}")[0].trim();
        if (changedValue == ""){
          changedValue = 0
        }

        calculationKey[labelsForCalculations[key]] = changedValue;
        
      }

      for (const element of calculationField) {
        searchKey = ""
        var matched = false;
        var calculationFieldID = document.getElementById(element["id"]);

        //console.log(element);
        for (const [key, value] of Object.entries(element["monitor_labels"])) {
          for (const [key2, value2] of Object.entries(calculationKey)) {
            if (key2 == value){
              searchKey += key2 + value2 + "-"
            }
          }
        }

        if (searchKey.endsWith('-')) {
          searchKey = searchKey.slice(0, -1);
        }

        for (const [key3, value3] of Object.entries(element["choices"])) {
          if (value3.includes(searchKey)){
            calculationFieldID.value = key3;
            matched = true;
            break;
          }
        }

        if (matched == false){
          calculationFieldID.value = "";
        }
      }
    }

    for (var key in labelsForCalculations) {
      const field = document.getElementById(key);
      if (field) {
        field.addEventListener('change', handleFieldChange);
      }
    }

  </script>
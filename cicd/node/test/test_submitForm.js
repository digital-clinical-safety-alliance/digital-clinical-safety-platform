// test_submitForm.js

const { test } = QUnit;

// Mock the required DOM elements for testing
global.document = {
  getElementById: function (id) {
    if (id === 'id_form') {
      return {
        submit: function () {
          this.submitted = true;
        },
      };
    } else if (id === 'id_button') {
      return {
        disabled: false,
      };
    } else if (id === 'loading-icon') {
      return {
        classList: {
          contains: function (className) {
            return className === 'show';
          },
          add: function (className) {
            // Implement the add method if needed
          },
        },
      };
    }
  },
};

// Mock the global window object for QUnit's async support
global.window = global;

const submitForm = require('../functions/submitForm.js');

test('submitForm Test', function (assert) {
    // Call the function that manipulates the DOM
    submitForm();

    // Get references to the mocked DOM elements
    const form = global.document.getElementById('id_form');
    const submitBtn = global.document.getElementById('id_button');
    const loadingIcon = global.document.getElementById('loading-icon');

    // Assertions
    assert.ok(submitBtn.disabled, 'Button should be disabled');
    assert.ok(loadingIcon.classList.contains('show'), 'Loading icon should be visible');
    
    // Simulate the form submission
    // This could be further tested depending on the actual behavior you expect
    // For simplicity, here we are just checking if the form has been submitted
    assert.ok(form.submitted, 'Form should be submitted');
});
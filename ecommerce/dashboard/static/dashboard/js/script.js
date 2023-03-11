// Function: toggleMenu() to responsive menu
function toggleMenu() {
    let toggle = document.querySelector('.toggle');
    let navigation = document.querySelector('.navigation');
    let main = document.querySelector('.main');
    toggle.classList.toggle('active');
    navigation.classList.toggle('active');
    main.classList.toggle('active');

    // Save the state of the toggle to local storage
    localStorage.setItem('menuToggleState', toggle.classList.contains('active'));
}

// Check the state of the toggle on page load
let savedToggleState = localStorage.getItem('menuToggleState');
if (savedToggleState === 'true') {
    toggleMenu();
}
//
// // Code select all checkbox and select a checkbox in Django admin and save it in to user.ids=[]
// let selectAllCheckbox = document.getElementById("select-all");
// let checkboxes = document.querySelectorAll("input[type=checkbox]:not(#select-all)");
//
// selectAllCheckbox.addEventListener("click", function () {
//     for (let i = 0; i < checkboxes.length; i++) {
//         checkboxes[i].checked = selectAllCheckbox.checked;
//     }
// });
//
//
// let user_ids = [];
// let user_ids_input = document.getElementById("user_ids");
// for (let i = 0; i < checkboxes.length; i++) {
//     checkboxes[i].addEventListener("click", function () {
//         if (this.checked) {
//             user_ids.push(this.value);
//         } else {
//             user_ids = user_ids.filter(function (item) {
//                 return item !== this.value;
//             });
//         }
//         user_ids_input.value = user_ids;
//     });
// }
// Wait for the DOM to finish loading before running the script
// document.addEventListener("DOMContentLoaded", function() {
//   // Get the form and the delete selected button
//     let form = document.getElementById("delete-form");
//     let deleteBtn = document.querySelector("[data-submit-form]");
//
//   // Listen for the click event on the delete selected button
//   deleteBtn.addEventListener("click", function(event) {
//     // Get the selected checkboxes
//     let checkboxes = document.querySelectorAll(".select-checkbox:checked");
//     // If no checkboxes are selected, prevent the form submission
//     if (checkboxes.length === 0) {
//       event.preventDefault();
//       alert("Please select at least one customer to delete.");
//     } else {
//       // Update the action attribute of the form
//       let customerIds = Array.from(checkboxes).map(function(checkbox) {
//         return checkbox.value;
//       });
//       form.action = "/dashboard/delete_selected_customer/" + customerIds.join("+") + "/";
//       // Submit the form
//       form.submit();
//     }
//   });
// });

// Wait for the DOM to finish loading before running the script
document.addEventListener("DOMContentLoaded", function() {
  // Get the form and the delete selected button
  let form = document.getElementById("delete-form");
  let deleteBtn = document.querySelector("[data-submit-form]");
  let selectAllCheckbox = document.getElementById("select-all");

  // Listen for the click event on the delete selected button
  deleteBtn.addEventListener("click", function(event) {
    // Get the selected checkboxes
    let checkboxes = document.querySelectorAll(".select-checkbox:checked");
    // If no checkboxes are selected, prevent the form submission
    if (checkboxes.length === 0) {
      event.preventDefault();
      alert("Please select at least one customer to delete.");
    } else {
      // Update the action attribute of the form
      let customerIds = Array.from(checkboxes).map(function(checkbox) {
        return checkbox.value;
      });
      form.action = "/dashboard/delete_selected_customer/" + customerIds.join("+") + "/";
      // Submit the form
      form.submit();
    }
  });

  // Listen for the click event on the select-all checkbox
  selectAllCheckbox.addEventListener("click", function() {
    // Get all the customer checkboxes
    let customerCheckboxesAll = document.querySelectorAll(".select-checkbox");
    // Set their checked property based on the select-all checkbox
    customerCheckboxesAll.forEach(function(checkbox) {
      checkbox.checked = selectAllCheckbox.checked;
        let customerIds = Array.from(customerCheckboxesAll).map(function(checkbox) {
            return checkbox.value;
        });
        form.action = "/dashboard/delete_selected_customer/" + customerIds.join("+") + "/";
        form.submit();
    });
  });
});
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

// Code select all checkbox and select a checkbox in Django admin and save it in to user.ids=[]
let selectAllCheckbox = document.getElementById("select-all");
let checkboxes = document.querySelectorAll("input[type=checkbox]:not(#select-all)");

selectAllCheckbox.addEventListener("click", function () {
    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = selectAllCheckbox.checked;
    }
});

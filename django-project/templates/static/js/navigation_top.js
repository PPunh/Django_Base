
function w3_open() {
document.getElementById("mySidebar").style.display = "block";
}

function w3_close() {
document.getElementById("mySidebar").style.display = "none";
}

function toggleDropdown(id) {
const el = document.getElementById(id);
el.classList.toggle("w3-show");
el.classList.toggle("w3-hide");
}

// Simple dropdown toggle function for navigation
function toggleNavDropdown(event, element) {
    event.stopPropagation();
    event.preventDefault();
    
    // Remove active class from all dropdowns
    const allDropdowns = document.querySelectorAll('.w3-dropdown-hover');
    allDropdowns.forEach(function(dropdown) {
        if (dropdown !== element) {
            dropdown.classList.remove('dropdown-active');
        }
    });
    
    // Toggle active class on clicked dropdown
    element.classList.toggle('dropdown-active');
}

// Close dropdowns when clicking outside
document.addEventListener('click', function() {
    const allDropdowns = document.querySelectorAll('.w3-dropdown-hover');
    allDropdowns.forEach(function(dropdown) {
        dropdown.classList.remove('dropdown-active');
    });
});

// Prevent dropdown from closing when clicking inside
document.addEventListener('DOMContentLoaded', function() {
    const dropdownContents = document.querySelectorAll('.w3-dropdown-content');
    dropdownContents.forEach(function(content) {
        content.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize select elements
    var elems = document.querySelectorAll('select');
    M.FormSelect.init(elems);

    // Toggle Advanced Search
    var toggleButton = document.getElementById('toggle-advanced-search');
    var advancedSearch = document.getElementById('advanced-search-filters');

    toggleButton.addEventListener('click', function() {
        if (advancedSearch.style.display === "none") {
            advancedSearch.style.display = "block";
        } else {
            advancedSearch.style.display = "none";
        }
    });
});
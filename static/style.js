// Function to filter menu items by category
function filterMenu(category) {
    // First, hide all menu categories
    const allCategories = document.querySelectorAll('.menu-category');
    allCategories.forEach(categoryElement => {
        categoryElement.style.display = 'none';
    });

    // Show the selected category
    const selectedCategory = document.getElementById(`category-${category}`);
    if (selectedCategory) {
        selectedCategory.style.display = 'block';
    }
}

// Optionally, you can display all categories by default when the page loads
document.addEventListener("DOMContentLoaded", function() {
    const allCategories = document.querySelectorAll('.menu-category');
    allCategories.forEach(categoryElement => {
        categoryElement.style.display = 'block'; // Show all categories initially
    });
});
// Function to handle menu item click


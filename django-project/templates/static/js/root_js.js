// Fixed Onlcile URL
// when using "data-url"
document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.row-link');
    rows.forEach(row => {
        row.addEventListener('click', function() {
            window.location.href = this.dataset.url;
        });
    });
});

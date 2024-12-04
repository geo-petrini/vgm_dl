// Function to set the theme preference in localStorage
function setThemePreference(theme) {
    localStorage.setItem('theme', theme);
}

$(document).ready(function () {
    // Retrieve the saved theme preference from localStorage
    var savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        $("#theme-css").attr('href', '/css/vendor/' + savedTheme + '/bootstrap-' + savedTheme + '.min.css');
    }

    $(".theme-item").click(function () {
        var theme = $(this).data('theme');
        $("#theme-css").attr('href', '/css/vendor/' + theme + '/bootstrap-' + theme + '.min.css');
        setThemePreference(theme); // Save the selected theme preference
        $(".theme-menu").removeClass("show");
    });

    $(document).on("click", function (e) {
        if (!$(e.target).closest(".dropdown").length) {
            $(".theme-menu").removeClass("show");
        }
    });
});

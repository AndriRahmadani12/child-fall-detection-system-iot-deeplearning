const toggleButton = document.getElementById("dark-mode-toggle");
const sunIcon = document.getElementById("sun-icon");
const moonIcon = document.getElementById("moon-icon");

// Check the current theme and set accordingly
if (localStorage.getItem("theme") === "dark") {
    document.documentElement.classList.add("dark");
    moonIcon.classList.add("hidden");
    sunIcon.classList.remove("hidden");
}

// Event listener for toggle button
toggleButton.addEventListener("click", () => {
    const isDarkMode = document.documentElement.classList.contains("dark");

    if (isDarkMode) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
        moonIcon.classList.remove("hidden");
        sunIcon.classList.add("hidden");
    } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
        moonIcon.classList.add("hidden");
        sunIcon.classList.remove("hidden");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.getElementById("navbar");

    window.addEventListener("scroll", function () {
        if (window.scrollY > 50) {
            navbar.classList.add("shadow-lg", "py-2"); // Tambahkan shadow besar dan kecilkan navbar
            navbar.classList.remove("shadow-sm", "lg:py-6");
        } else if (window.scrollY === 0) {
            navbar.classList.add("lg:py-6");
            navbar.classList.remove("shadow-md", "shadow-lg"); // Kembalikan ke ukuran awal
        }
    });
});

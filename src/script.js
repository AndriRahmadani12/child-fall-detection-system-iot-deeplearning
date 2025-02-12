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

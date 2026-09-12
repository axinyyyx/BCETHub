// Theme Toggle Logic
const themeToggleBtn = document.getElementById('theme-toggle');
const htmlElement = document.documentElement;

const getPreferredTheme = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) return savedTheme;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
};

const updateThemeIcon = (theme) => {
    if (!themeToggleBtn) return;
    const iconContainer = themeToggleBtn.querySelector('.theme-icon');
    if (iconContainer) {
        if (theme === 'light') {
            iconContainer.setAttribute('data-lucide', 'sun');
        } else {
            iconContainer.setAttribute('data-lucide', 'moon');
        }
        if (window.lucide) {
            lucide.createIcons();
        }
    }
};

const setTheme = (theme) => {
    htmlElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
};

setTheme('dark');

// if (themeToggleBtn) {
//     themeToggleBtn.addEventListener('click', (e) => {
//         e.preventDefault();
//         const currentTheme = htmlElement.getAttribute('data-theme');
//         const newTheme = currentTheme === 'light' ? 'dark' : 'light';
//         setTheme(newTheme);
//     });
// }

// popup close when clicking outside the search container
document.addEventListener('click', function(event) {
    const searchContainer = document.querySelector('.search-container');
    const popup = document.getElementById('live-search-popup');
    if (popup && searchContainer && !searchContainer.contains(event.target)) {
        popup.innerHTML = '';
    }
});

// disable developer tools
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

document.addEventListener('keydown', function(e) {
    if (
        e.key === 'F12' ||
        (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j' || e.key === 'C' || e.key === 'c')) ||
        (e.ctrlKey && (e.key === 'U' || e.key === 'u'))
    ) {
        e.preventDefault();
        return false;
    }
});

// Theme toggle setup
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

// Close search popup
document.addEventListener('click', function(event) {
    const searchContainer = document.querySelector('.search-container');
    const popup = document.getElementById('live-search-popup');
    if (popup && searchContainer && !searchContainer.contains(event.target)) {
        popup.innerHTML = '';
    }
});

// Protect keyboard shortcuts
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

// Disable keyboard zoom
document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && ["+", "-", "=", "0"].includes(e.key)) {
        e.preventDefault();
    }
});

// Disable pinch zoom on mobile
document.addEventListener("touchstart", function (e) {
    if (e.touches.length > 1) {
        e.preventDefault();
    }
}, { passive: false });

document.addEventListener("touchmove", function (e) {
    if (e.touches.length > 1) {
        e.preventDefault();
    }
}, { passive: false });

// Disable double-tap zoom
let lastTouchEnd = 0;

document.addEventListener("touchend", function (e) {
    const now = Date.now();

    if (now - lastTouchEnd <= 300) {
        e.preventDefault();
    }

    lastTouchEnd = now;
}, { passive: false });

// Disable Safari gesture zoom
["gesturestart", "gesturechange", "gestureend"].forEach(function (event) {
    document.addEventListener(event, function (e) {
        e.preventDefault();
    }, { passive: false });
});
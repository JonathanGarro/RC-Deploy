'use strict';
{
    const themeStorageKey = 'django.admin.theme';

    // Get the theme toggle button element if it exists
    const getToggleButton = () => {
        return document.querySelector('.theme-toggle');
    };

    // Get the current theme from localStorage or system preference
    const getTheme = () => {
        if (localStorage.getItem(themeStorageKey)) {
            return localStorage.getItem(themeStorageKey);
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    // Set the theme by adding or removing the 'theme-dark' class on the body
    const setTheme = (theme) => {
        const root = document.documentElement;
        if (theme === 'dark') {
            root.classList.add('theme-dark');
        } else {
            root.classList.remove('theme-dark');
        }
        localStorage.setItem(themeStorageKey, theme);

        // Update the toggle button icon if it exists
        const toggleButton = getToggleButton();
        if (toggleButton) {
            toggleButton.innerHTML = theme === 'dark' 
                ? '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>'
                : '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
        }
    };

    // Toggle between light and dark themes
    const toggleTheme = () => {
        const currentTheme = getTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    };

    // Initialize theme
    const initTheme = () => {
        // Set initial theme
        setTheme(getTheme());

        // Create and add theme toggle button if it doesn't exist
        if (!getToggleButton() && document.getElementById('user-tools')) {
            const userTools = document.getElementById('user-tools');
            const toggleButton = document.createElement('button');
            toggleButton.className = 'theme-toggle';
            toggleButton.setAttribute('type', 'button');
            toggleButton.setAttribute('aria-label', 'Toggle light/dark theme');
            toggleButton.innerHTML = getTheme() === 'dark' 
                ? '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>'
                : '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
            toggleButton.addEventListener('click', toggleTheme);
            userTools.appendChild(toggleButton);
        }

        // Add event listener for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem(themeStorageKey)) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    };

    // Run initialization when DOM is loaded
    if (document.readyState !== 'loading') {
        initTheme();
    } else {
        document.addEventListener('DOMContentLoaded', initTheme);
    }
}

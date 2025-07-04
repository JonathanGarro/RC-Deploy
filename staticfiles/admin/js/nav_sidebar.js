'use strict';
{
    const toggleNavSidebar = document.getElementById('toggle-nav-sidebar');
    if (toggleNavSidebar !== null) {
        const navSidebar = document.getElementById('nav-sidebar');
        const main = document.getElementById('main');
        const sidebarStorageKey = 'django.admin.navSidebarIsCollapsed';
        
        // Get the sidebar collapsed state from localStorage
        const getIsNavSidebarCollapsed = () => {
            return localStorage.getItem(sidebarStorageKey) === 'true';
        };
        
        // Set the sidebar collapsed state in localStorage
        const setIsNavSidebarCollapsed = (isCollapsed) => {
            localStorage.setItem(sidebarStorageKey, isCollapsed);
        };
        
        // Toggle the sidebar collapsed state
        const toggleNavSidebarCollapsed = () => {
            const isCollapsed = !getIsNavSidebarCollapsed();
            setIsNavSidebarCollapsed(isCollapsed);
            
            if (isCollapsed) {
                document.body.classList.add('nav-sidebar-collapsed');
            } else {
                document.body.classList.remove('nav-sidebar-collapsed');
            }
        };
        
        // Initialize the sidebar state
        const initNavSidebar = () => {
            if (getIsNavSidebarCollapsed()) {
                document.body.classList.add('nav-sidebar-collapsed');
            } else {
                document.body.classList.remove('nav-sidebar-collapsed');
            }
            
            toggleNavSidebar.addEventListener('click', toggleNavSidebarCollapsed);
        };
        
        // Add toggle button to the sidebar
        const createToggleButton = () => {
            // Create the toggle button if it doesn't exist
            if (!toggleNavSidebar.innerHTML.trim()) {
                toggleNavSidebar.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18M3 6h18M3 18h18"/></svg>';
                toggleNavSidebar.setAttribute('aria-label', 'Toggle navigation');
                toggleNavSidebar.setAttribute('title', 'Toggle navigation');
            }
        };
        
        // Make the sidebar sticky on scroll
        const handleStickyNav = () => {
            const adminForm = document.querySelector('.change-form, .changelist');
            if (adminForm) {
                const header = document.getElementById('header');
                const headerHeight = header ? header.offsetHeight : 0;
                
                const handleScroll = () => {
                    if (window.scrollY > headerHeight) {
                        navSidebar.classList.add('sticky');
                        navSidebar.style.top = '0';
                    } else {
                        navSidebar.classList.remove('sticky');
                        navSidebar.style.top = '';
                    }
                };
                
                window.addEventListener('scroll', handleScroll);
                handleScroll();
            }
        };
        
        // Initialize everything
        createToggleButton();
        initNavSidebar();
        handleStickyNav();
    }
}
/**
 * Admin Dashboard Shared Functions
 * Common Alpine.js utilities and helpers
 */

// Global authentication wrapper for fetch requests
window.authFetch = function(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return fetch(url, options);
};

// Global alert function
window.showAlert = function(message, type = 'success') {
    window.dispatchEvent(new CustomEvent('show-alert', {
        detail: { message, type }
    }));
};

// Date formatting helper
window.formatDate = function(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

// DateTime formatting helper
window.formatDateTime = function(dateString) {
    return new Date(dateString).toLocaleString('en-US');
};

// Handle logout
window.handleLogout = function() {
    localStorage.removeItem('access_token');
    window.location.href = '/';
};

// CSV export helper
window.exportToCSV = function(data, headers, filename = 'export.csv') {
    const csv = [headers, ...data].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
};
